import type { DeviceStatus } from '../types/camera';

interface Props {
  status: DeviceStatus;
}

const statusConfig = {
  online: { color: 'bg-green-500', text: 'En línea', animate: 'animate-pulse' },
  offline: { color: 'bg-red-500', text: 'Fuera de línea', animate: '' },
  warning: { color: 'bg-yellow-500', text: 'Advertencia', animate: 'animate-pulse' },
  unreachable: { color: 'bg-gray-500', text: 'Inalcanzable', animate: '' },
  maintenance: { color: 'bg-blue-500', text: 'Mantenimiento', animate: '' },
};

export function StatusBadge({ status }: Props) {
  const config = statusConfig[status];
  
  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${config.color} ${config.animate}`} />
      <span className="text-sm font-medium">{config.text}</span>
    </div>
  );
}