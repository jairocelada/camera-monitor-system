import type { Camera } from '../types/camera';
import { StatusBadge } from './StatusBadge';
import { Wifi, MapPin, Clock, Activity } from 'lucide-react';

interface Props {
  camera: Camera;
  onCheck: (id: string) => void;
}

export function CameraCard({ camera, onCheck }: Props) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
          <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
            <Wifi size={14} />
            {camera.ip_address}
          </p>
        </div>
        <StatusBadge status={camera.status} />
      </div>
      
      <div className="space-y-2 text-sm text-gray-300 mb-4">
        {camera.location && (
          <p className="flex items-center gap-2">
            <MapPin size={14} className="text-gray-500" />
            {camera.location}
          </p>
        )}
        {camera.last_seen && (
          <p className="flex items-center gap-2">
            <Clock size={14} className="text-gray-500" />
            Última vez: {new Date(camera.last_seen).toLocaleString()}
          </p>
        )}
        {camera.response_time_ms && (
          <p className="flex items-center gap-2">
            <Activity size={14} className="text-gray-500" />
            Latencia: {camera.response_time_ms}ms
          </p>
        )}
      </div>
      
      <button
        onClick={() => onCheck(camera.id)}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition-colors text-sm font-medium"
      >
        Verificar ahora
      </button>
    </div>
  );
}