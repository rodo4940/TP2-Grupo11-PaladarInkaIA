import type { HealthResponse } from '../types/api';

const API_URL = import.meta.env.VITE_API_URL;

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/v1/health`);

  if (!response.ok) {
    throw new Error('API health check failed');
  }

  return response.json() as Promise<HealthResponse>;
}
