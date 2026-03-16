export type DeviceStatus = 'online' | 'offline' | 'warning' | 'unreachable' | 'maintenance';

export interface Camera {
  id: string;
  name: string;
  ip_address: string;
  status: DeviceStatus;
  last_seen: string | null;
  response_time_ms: number | null;
  location: string | null;
  brand: string | null;
  packet_loss_percent: number;
}

export interface ConnectivityLog {
  id: string;
  camera_id: string;
  timestamp: string;
  status: DeviceStatus;
  response_time_ms: number | null;
  packet_loss: number;
}