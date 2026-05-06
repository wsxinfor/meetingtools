import http from './http'

export interface TranscriptSegment {
  id: string
  meeting_id: string
  audio_file_id: string
  segment_index: number
  start_ms: number
  end_ms: number
  speaker_label: string | null
  raw_text: string | null
  corrected_text: string | null
  confidence: number | null
  created_at: string
  updated_at: string
}

export async function listSegments(meetingId: string): Promise<TranscriptSegment[]> {
  const res = await http.get(`/meetings/${meetingId}/transcript-segments`)
  return res.data.data
}

export async function updateSegment(
  segmentId: string,
  payload: { corrected_text?: string | null; speaker_label?: string | null },
): Promise<TranscriptSegment> {
  const res = await http.put(`/transcript-segments/${segmentId}`, payload)
  return res.data.data
}

export async function saveCorrectedText(
  meetingId: string,
  correctedText: string,
): Promise<void> {
  await http.put(`/meetings/${meetingId}/corrected-text`, { corrected_text: correctedText })
}
