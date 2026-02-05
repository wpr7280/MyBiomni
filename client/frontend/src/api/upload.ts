import { agentApiClient } from './agentClient';

export interface UploadResult {
  id: number;
  filename: string;
  path: string;
  size: number;
  mimeType?: string;
}

export async function uploadAttachment(conversationId: number, file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversation_id', String(conversationId));

  const response = await agentApiClient.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data as UploadResult;
}
