/**
 * merge_server.js
 * Hybrid Transcode + Stream Copy FFmpeg Server
 * 
 * FIX FOR YOUTUBE "PROCESSING" HANGS:
 * We first transcode the single Pexels clip (15s) to a pristine MPEG-TS file, standardizing 
 * the framerate and completely wiping corrupted Video/Audio timestamps.
 * THEN we use zero-cpu stream copy to concatenate that pristine TS file 15 times, 
 * multiplexing it with the Deepgram audio into a final MP4 +faststart.
 */

const express = require('express');
const multer  = require('multer');
const { execSync } = require('child_process');
const fs = require('fs');
const { randomUUID } = require('crypto');

const app  = express();
const PORT = process.env.MERGE_SERVER_PORT || 3000;
const upload = multer({ dest: '/tmp/' });

app.post('/merge', upload.fields([
  { name: 'video', maxCount: 1 },
  { name: 'audio', maxCount: 1 }
]), (req, res) => {
  const id        = randomUUID();
  const videoPath = req.files?.video?.[0]?.path;
  const audioPath = req.files?.audio?.[0]?.path;
  const tempTsPath = `/tmp/temp_${id}.ts`;
  const listPath  = `/tmp/list_${id}.txt`;
  let outPath     = `/tmp/merged_${id}.mp4`;

  if (!videoPath || !audioPath) {
    return res.status(400).json({ error: 'Missing video or audio' });
  }

  try {
    console.log(`[${id}] Step 1: Transcoding 15s Pexels loop to clean MPEG-TS...`);
    // Scale to standard 720p Shorts, force 30fps, write to TS segment.
    // This is computationally small because the source video is only ~15 seconds.
    execSync(`ffmpeg -i "${videoPath}" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" -r 30 -c:v libx264 -preset ultrafast -crf 28 -f mpegts -y "${tempTsPath}"`, { stdio: 'pipe' });

    console.log(`[${id}] Step 2: Generating concatenation list...`);
    let listContent = '';
    // Loop 15 times (15 * 15s = 3.75 minutes max support)
    for(let i=0; i<15; i++) {
        listContent += `file '${tempTsPath}'\n`;
    }
    fs.writeFileSync(listPath, listContent);

    console.log(`[${id}] Step 3: Concatenating TS and multiplexing audio...`);
    // Stream copy the video (0% CPU impact) and only encode the Deepgram audio, trim to shortest.
    execSync(
      `ffmpeg -f concat -safe 0 -i "${listPath}" -i "${audioPath}" ` +
      `-map 0:v:0 -map 1:a:0 ` +
      `-c:v copy -c:a aac -b:a 128k ` +
      `-shortest -movflags +faststart -y "${outPath}"`,
      { stdio: 'pipe', timeout: 120_000 }
    );

    console.log(`[${id}] Success! Sending pristine MP4 stream to n8n.`);
    const merged = fs.readFileSync(outPath);
    res.set('Content-Type', 'video/mp4');
    res.set('Content-Disposition', `attachment; filename="merged_${id}.mp4"`);
    res.send(merged);

  } catch (err) {
    console.error(`[${id}] FFmpeg error:`, err.stderr?.toString() || err.message);
    res.status(500).json({ error: 'FFmpeg failed', detail: err.message });
  } finally {
    console.log(`[${id}] Cleaning up temporary assets.`);
    [videoPath, audioPath, tempTsPath, listPath, outPath].forEach(f => {
      try { if (f && fs.existsSync(f)) fs.unlinkSync(f); } catch (_) {}
    });
  }
});

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

app.listen(PORT, 10000, () => {
  console.log(`[merge_server] Running on port ${PORT}`);
});
