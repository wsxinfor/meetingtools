import http from './http'

export interface Meeting {
  id: string
  customer_id: string | null
  project_id: string | null
  title: string
  meeting_type: string | null
  meeting_time: string | null
  participants: string[] | null
  speaker_map: Record<string, string> | null
  status: string
  created_at: string
  updated_at: string
}

export interface MeetingDetail extends Meeting {
  raw_text: string | null
  corrected_text: string | null
  summary_text: string | null
  error_message: string | null
}

export interface MeetingCreate {
  title: string
  meeting_type?: string
  customer_id?: string
  project_id?: string
  meeting_time?: string
  participants?: string[]
}

export interface MeetingUpdate {
  title?: string
  meeting_type?: string
  customer_id?: string | null
  project_id?: string | null
  meeting_time?: string | null
  participants?: string[]
  status?: string
}

export interface MeetingListQuery {
  keyword?: string
  customer_id?: string
  project_id?: string
  status?: string
  page?: number
  page_size?: number
}

export interface PagedMeetings {
  total: number
  items: Meeting[]
}

export async function listMeetings(query: MeetingListQuery = {}): Promise<PagedMeetings> {
  const res = await http.get<{ code: number; data: PagedMeetings }>('/meetings', { params: query })
  return res.data.data
}

export async function getMeeting(id: string): Promise<MeetingDetail> {
  const res = await http.get<{ code: number; data: MeetingDetail }>(`/meetings/${id}`)
  return res.data.data
}

export async function createMeeting(data: MeetingCreate): Promise<Meeting> {
  const res = await http.post<{ code: number; data: Meeting }>('/meetings', data)
  return res.data.data
}

export async function updateMeeting(id: string, data: MeetingUpdate): Promise<MeetingDetail> {
  const res = await http.put<{ code: number; data: MeetingDetail }>(`/meetings/${id}`, data)
  return res.data.data
}

export async function deleteMeeting(id: string): Promise<void> {
  await http.delete(`/meetings/${id}`)
}

export async function updateSpeakerMap(
  id: string,
  speakerMap: Record<string, string>,
): Promise<MeetingDetail> {
  const res = await http.patch<{ code: number; data: MeetingDetail }>(
    `/meetings/${id}/speaker-map`,
    { speaker_map: speakerMap },
  )
  return res.data.data
}
