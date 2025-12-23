import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

function History() {
  const navigate = useNavigate();
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSnapshots();
  }, []);

  const loadSnapshots = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/history/snapshots`);
      setSnapshots(res.data.reverse());
    } catch (error) {
      console.error('Error loading snapshots:', error);
      toast.error('Erreur lors du chargement de l\'historique');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const chartData = snapshots.map(s => ({
    date: formatDate(s.timestamp),
    'Total': s.total_value_eur,
    'Crypto': s.crypto_value_eur,
    'Actions': s.stocks_value_eur,
    'Pièces': s.coins_value_eur
  }));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#09090B]">
        <div className="text-[#A1A1AA] font-mono">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090B] p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Button 
            onClick={() => navigate('/')} 
            variant="outline" 
            className="border-[#27272A] text-white hover:bg-[#18181B]"
            data-testid="back-button"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour
          </Button>
          <h1 className="text-4xl md:text-5xl font-bold font-['Chivo'] text-[#FAFAFA] tracking-tight" data-testid="history-title">
            Historique du Portfolio
          </h1>
        </div>

        {snapshots.length === 0 ? (
          <Card className="bg-[#18181B] border border-[#27272A] p-12">
            <div className="text-center text-[#A1A1AA]">
              <p className="text-lg mb-4">Aucun instantané disponible</p>
              <p className="text-sm">Créez un instantané depuis le dashboard pour suivre l'évolution de votre portfolio</p>
            </div>
          </Card>
        ) : (
          <Card className="bg-[#18181B] border border-[#27272A] p-6" data-testid="history-chart">
            <h2 className="text-2xl font-['Chivo'] font-semibold mb-6">Évolution de la valeur</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                <XAxis dataKey="date" stroke="#A1A1AA" style={{ fontSize: '12px' }} />
                <YAxis stroke="#A1A1AA" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#18181B', 
                    border: '1px solid #27272A',
                    borderRadius: '4px',
                    color: '#FAFAFA'
                  }}
                />
                <Legend wrapperStyle={{ color: '#A1A1AA' }} />
                <Line type="monotone" dataKey="Total" stroke="#FAFAFA" strokeWidth={2} />
                <Line type="monotone" dataKey="Crypto" stroke="#6366F1" strokeWidth={2} />
                <Line type="monotone" dataKey="Actions" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="Pièces" stroke="#EAB308" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        )}

        {snapshots.length > 0 && (
          <Card className="bg-[#18181B] border border-[#27272A] p-6 mt-6">
            <h2 className="text-2xl font-['Chivo'] font-semibold mb-6">Détails des instantanés</h2>
            <div className="space-y-3">
              {snapshots.slice().reverse().map((snapshot, idx) => (
                <div 
                  key={snapshot.id} 
                  className="flex justify-between items-center p-4 bg-[#09090B] border border-[#27272A]"
                  data-testid={`snapshot-${idx}`}
                >
                  <div className="text-[#A1A1AA]">{formatDate(snapshot.timestamp)}</div>
                  <div className="text-right">
                    <div className="font-mono text-[#FAFAFA] font-semibold">
                      {snapshot.total_value_eur.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
                    </div>
                    <div className="text-sm text-[#A1A1AA]">
                      Crypto: {snapshot.crypto_value_eur.toFixed(2)}€ | 
                      Actions: {snapshot.stocks_value_eur.toFixed(2)}€ | 
                      Pièces: {snapshot.coins_value_eur.toFixed(2)}€
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

export default History;