/**
 * merge_server.js
 * Lightweight Express server that merges a video file and an audio file
 * using FFmpeg, then returns the merged MP4 as a binary response.
 *
 * Called by n8n via HTTP POST to http://localhost:3000/merge
 * Body: multipart/form-data with fields:
 *   - video: the raw video binary (from Pexels download)
 *   - audio: the raw audio binary (from Deepgram)
 */

const express = require('express');
const multer  = require('multer');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { randomUUID } = require('crypto');

const app  = express();
const PORT = process.env.MERGE_SERVER_PORT || 3000;

// Store uploads in /tmp (ephemeral, fine for Render free tier)
const upload = multer({ dest: '/tmp/' });

app.post('/merge', upload.fields([
  { name: 'video', maxCount: 1 },
  { name: 'audio', maxCount: 1 }
]), (req, res) => {
  const id        = randomUUID();
  const videoPath = req.files?.video?.[0]?.path;
  const audioPath = req.files?.audio?.[0]?.path;
  const outPath   = `/tmp/merged_${id}.mp4`;

  if (!videoPath || !audioPath) {
    return res.status(400).json({ error: 'Both video and audio fields are required.' });
  }

  try {
    /**
     * FFmpeg command breakdown:
     * -i videoPath        → input video (silent Pexels clip)
     * -i audioPath        → input audio (Deepgram MP3/WAV)
     * -map 0:v:0          → take video stream from first input
     * -map 1:a:0          → take audio stream from second input
     * -c:v copy           → do NOT re-encode video (fast, no quality loss)
     * -c:a aac            → encode audio to AAC (YouTube-compatible)
     * -shortest           → trim to the shorter of video/audio
     * -movflags +faststart → put MOOV atom at front (better YouTube ingestion)
     * -y                  → overwrite output file without asking
     */
    execSync(
      `ffmpeg -stream_loop -1 -i "${videoPath}" -i "${audioPath}" ` +
      `-map 0:v:0 -map 1:a:0 ` +
      `-c:v copy -c:a aac -b:a 128k ` +
      `-shortest -movflags +faststart -fflags +genpts ` +
      `-y "${outPath}"`,
      { stdio: 'pipe', timeout: 120_000 }
    );

    // Stream merged file back to n8n
    const merged = fs.readFileSync(outPath);
    res.set('Content-Type', 'video/mp4');
    res.set('Content-Disposition', `attachment; filename="merged_${id}.mp4"`);
    res.send(merged);

  } catch (err) {
    console.error('[merge_server] FFmpeg error:', err.stderr?.toString() || err.message);
    res.status(500).json({ error: 'FFmpeg merge failed.', detail: err.message });
  } finally {
    // Clean up temp files
    [videoPath, audioPath, outPath].forEach(f => {
      try { if (f) fs.unlinkSync(f); } catch (_) {}
    });
  }
});

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => {
  console.log(`[merge_server] Running on port ${PORT}`);
});
