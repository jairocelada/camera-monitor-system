import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cameraApi, statsApi } from '../services/api';
import { CameraCard } from '../components/CameraCard';
import { Activity, Plus, RefreshCw } from 'lucide-react';
import { useState } from 'react';

export function Dashboard() {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Queries
  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: () => cameraApi.getAll().then(r => r.data),
    refetchInterval: 10000, // Refrescar cada 10 segundos
  });
  
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.getStats().then(r => r.data),
    refetchInterval: 10000,
  });
  
  // Mutations
  const checkMutation = useMutation({
    mutationFn: (id: string) => cameraApi.checkNow(id),
    onSuccess: () => {
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ['cameras'] }), 2000);
    },
  });
  
  const checkAllMutation = useMutation({
    mutationFn: () => cameraApi.checkAll(),
  });
  
  if (isLoading) {
    return <div className="flex justify-center p-8">Cargando...</div>;
  }
  
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Activity className="text-blue-500" />
              Monitor de Cámaras IP
            </h1>
            <p className="text-gray-400 mt-1">Sistema de monitoreo en tiempo real</p>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => checkAllMutation.mutate()}
              disabled={checkAllMutation.isPending}
              className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <RefreshCw size={18} className={checkAllMutation.isPending ? 'animate-spin' : ''} />
              Verificar todas
            </button>
            
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus size={18} />
              Agregar cámara
            </button>
          </div>
        </div>
        
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatCard title="Total" value={stats.total_cameras} color="blue" />
            <StatCard title="En línea" value={stats.by_status?.online || 0} color="green" />
            <StatCard title="Fuera de línea" value={stats.by_status?.offline || 0} color="red" />
            <StatCard 
              title="Uptime" 
              value={`${stats.online_percent}%`} 
              color="purple" 
            />
          </div>
        )}
        
        {/* Grid de cámaras */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {cameras?.map(camera => (
            <CameraCard 
              key={camera.id} 
              camera={camera} 
              onCheck={(id) => checkMutation.mutate(id)}
            />
          ))}
        </div>
        
        {cameras?.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg">No hay cámaras registradas</p>
            <p className="text-sm mt-2">Haz clic en "Agregar cámara" para comenzar</p>
          </div>
        )}
      </div>
      
      {/* Modal agregar (simplificado) */}
      {showAddModal && <AddCameraModal onClose={() => setShowAddModal(false)} />}
    </div>
  );
}

function StatCard({ title, value, color }: { title: string; value: number | string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    green: 'bg-green-500/20 text-green-400 border-green-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
    purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  };
  
  return (
    <div className={`p-4 rounded-lg border ${colors[color]}`}>
      <p className="text-sm opacity-80">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

// Componente modal simplificado
function AddCameraModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: '', ip_address: '', location: '', brand: '' });
  
  const createMutation = useMutation({
    mutationFn: () => cameraApi.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] });
      onClose();
    },
  });
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-lg w-full max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">Agregar Cámara</h2>
        
        <div className="space-y-4">
          <input
            placeholder="Nombre (ej: Cámara Entrada Principal)"
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            value={form.name}
            onChange={e => setForm({...form, name: e.target.value})}
          />
          <input
            placeholder="IP Address (ej: 192.168.1.100)"
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            value={form.ip_address}
            onChange={e => setForm({...form, ip_address: e.target.value})}
          />
          <input
            placeholder="Ubicación (opcional)"
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            value={form.location}
            onChange={e => setForm({...form, location: e.target.value})}
          />
          <input
            placeholder="Marca (opcional)"
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            value={form.brand}
            onChange={e => setForm({...form, brand: e.target.value})}
          />
        </div>
        
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !form.name || !form.ip_address}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 rounded transition-colors"
          >
            {createMutation.isPending ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  );
}