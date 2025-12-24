import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { PlusCircle, TrendingUp, Bitcoin, DollarSign, Coins, Trash2, BarChart3, LogOut } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [cryptos, setCryptos] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [coins, setCoins] = useState([]);
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);

  // Add dialogs
  const [cryptoDialog, setCryptoDialog] = useState(false);
  const [stockDialog, setStockDialog] = useState(false);
  const [coinDialog, setCoinDialog] = useState(false);

  const [cryptoForm, setCryptoForm] = useState({ name: '', symbol: '', quantity: '', purchase_price: '' });
  const [stockForm, setStockForm] = useState({ name: '', symbol: '', quantity: '', purchase_price: '' });
  const [coinForm, setCoinForm] = useState({ name: '', url: '', css_selector: '', quantity: '' });

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, cryptosRes, stocksRes, coinsRes] = await Promise.all([
        axios.get(`${API}/portfolio/overview`, { withCredentials: true }),
        axios.get(`${API}/crypto`, { withCredentials: true }),
        axios.get(`${API}/stocks`, { withCredentials: true }),
        axios.get(`${API}/coins`, { withCredentials: true })
      ]);

      setOverview(overviewRes.data);
      setCryptos(cryptosRes.data);
      setStocks(stocksRes.data);
      setCoins(coinsRes.data);

      await loadPrices(cryptosRes.data, stocksRes.data, coinsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const loadPrices = async (cryptosList, stocksList, coinsList) => {
    const newPrices = {};
    
    for (const crypto of cryptosList) {
      try {
        const res = await axios.get(`${API}/crypto/${crypto.id}/price`, { withCredentials: true });
        newPrices[`crypto-${crypto.id}`] = res.data;
      } catch (error) {
        console.error(`Error loading price for ${crypto.symbol}:`, error);
      }
    }

    for (const stock of stocksList) {
      try {
        const res = await axios.get(`${API}/stocks/${stock.id}/price`, { withCredentials: true });
        newPrices[`stock-${stock.id}`] = res.data;
      } catch (error) {
        console.error(`Error loading price for ${stock.symbol}:`, error);
      }
    }

    for (const coin of coinsList) {
      try {
        const res = await axios.get(`${API}/coins/${coin.id}/price`, { withCredentials: true });
        newPrices[`coin-${coin.id}`] = res.data;
      } catch (error) {
        console.error(`Error loading price for ${coin.name}:`, error);
      }
    }

    setPrices(newPrices);
  };

  const handleAddCrypto = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/crypto`, {
        ...cryptoForm,
        quantity: parseFloat(cryptoForm.quantity),
        purchase_price: parseFloat(cryptoForm.purchase_price)
      }, { withCredentials: true });
      toast.success('Cryptomonnaie ajoutée avec succès');
      setCryptoDialog(false);
      setCryptoForm({ name: '', symbol: '', quantity: '', purchase_price: '' });
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout de la cryptomonnaie');
    }
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/stocks`, {
        ...stockForm,
        quantity: parseFloat(stockForm.quantity),
        purchase_price: parseFloat(stockForm.purchase_price)
      }, { withCredentials: true });
      toast.success('Action ajoutée avec succès');
      setStockDialog(false);
      setStockForm({ name: '', symbol: '', quantity: '', purchase_price: '' });
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout de l\'action');
    }
  };

  const handleAddCoin = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/coins`, {
        ...coinForm,
        quantity: parseFloat(coinForm.quantity)
      }, { withCredentials: true });
      toast.success('Pièce ajoutée avec succès');
      setCoinDialog(false);
      setCoinForm({ name: '', url: '', css_selector: '', quantity: '' });
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout de la pièce');
    }
  };

  const handleDelete = async (type, id) => {
    try {
      await axios.delete(`${API}/${type}/${id}`, { withCredentials: true });
      toast.success('Élément supprimé avec succès');
      loadData();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleSnapshot = async () => {
    try {
      await axios.post(`${API}/history/snapshot`, {}, { withCredentials: true });
      toast.success('Instantané créé avec succès');
    } catch (error) {
      toast.error('Erreur lors de la création de l\'instantané');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      toast.success('Déconnexion réussie');
      navigate('/login');
    } catch (error) {
      toast.error('Erreur lors de la déconnexion');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="loading-screen">
        <div className="text-[#A1A1AA] font-mono">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090B] p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold font-['Chivo'] text-[#FAFAFA] tracking-tight" data-testid="dashboard-title">
              Portfolio Tracker
            </h1>
            <p className="text-[#A1A1AA] mt-2">Suivez l'évolution de vos investissements</p>
          </div>
          <div className="flex gap-3">
            <Button 
              onClick={handleSnapshot} 
              variant="outline" 
              className="border-[#27272A] text-white hover:bg-[#18181B]"
              data-testid="snapshot-button"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Sauvegarder
            </Button>
            <Button 
              onClick={() => navigate('/history')} 
              variant="outline" 
              className="border-[#27272A] text-white hover:bg-[#18181B]"
              data-testid="history-button"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Historique
            </Button>
            <Button 
              onClick={handleLogout} 
              variant="outline" 
              className="border-[#27272A] text-white hover:bg-[#18181B]"
              data-testid="logout-button"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Déconnexion
            </Button>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6 mb-8">
          <Card className="bg-[#18181B] border border-[#27272A] p-6" data-testid="total-value-card">
            <div className="text-[#A1A1AA] text-sm mb-2">Valeur Totale</div>
            <div className="text-3xl font-mono font-semibold text-[#FAFAFA]">
              {overview?.total_value_eur?.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
            </div>
          </Card>
          <Card className="bg-[#18181B] border border-[#27272A] p-6" data-testid="crypto-value-card">
            <div className="flex items-center text-[#6366F1] text-sm mb-2">
              <Bitcoin className="w-4 h-4 mr-1" />
              Crypto
            </div>
            <div className="text-2xl font-mono font-semibold text-[#FAFAFA]">
              {overview?.crypto_value_eur?.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
            </div>
          </Card>
          <Card className="bg-[#18181B] border border-[#27272A] p-6" data-testid="stocks-value-card">
            <div className="flex items-center text-[#3B82F6] text-sm mb-2">
              <TrendingUp className="w-4 h-4 mr-1" />
              Actions
            </div>
            <div className="text-2xl font-mono font-semibold text-[#FAFAFA]">
              {overview?.stocks_value_eur?.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
            </div>
          </Card>
          <Card className="bg-[#18181B] border border-[#27272A] p-6" data-testid="coins-value-card">
            <div className="flex items-center text-[#EAB308] text-sm mb-2">
              <Coins className="w-4 h-4 mr-1" />
              Pièces
            </div>
            <div className="text-2xl font-mono font-semibold text-[#FAFAFA]">
              {overview?.coins_value_eur?.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
            </div>
          </Card>
        </div>

        {/* Assets Tabs */}
        <Tabs defaultValue="crypto" className="w-full">
          <TabsList className="bg-[#18181B] border border-[#27272A] mb-6">
            <TabsTrigger value="crypto" data-testid="crypto-tab">Cryptomonnaies ({overview?.crypto_count || 0})</TabsTrigger>
            <TabsTrigger value="stocks" data-testid="stocks-tab">Actions ({overview?.stocks_count || 0})</TabsTrigger>
            <TabsTrigger value="coins" data-testid="coins-tab">Pièces ({overview?.coins_count || 0})</TabsTrigger>
          </TabsList>

          {/* Crypto Tab */}
          <TabsContent value="crypto">
            <Card className="bg-[#18181B] border border-[#27272A] p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-['Chivo'] font-semibold">Cryptomonnaies</h2>
                <Dialog open={cryptoDialog} onOpenChange={setCryptoDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-white text-black hover:bg-gray-200" data-testid="add-crypto-button">
                      <PlusCircle className="w-4 h-4 mr-2" />
                      Ajouter
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#18181B] border border-[#27272A] text-white">
                    <DialogHeader>
                      <DialogTitle>Ajouter une cryptomonnaie</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddCrypto} className="space-y-4">
                      <div>
                        <Label>Nom</Label>
                        <Input 
                          value={cryptoForm.name} 
                          onChange={(e) => setCryptoForm({...cryptoForm, name: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="crypto-name-input"
                        />
                      </div>
                      <div>
                        <Label>Symbole (ex: BTC)</Label>
                        <Input 
                          value={cryptoForm.symbol} 
                          onChange={(e) => setCryptoForm({...cryptoForm, symbol: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="crypto-symbol-input"
                        />
                      </div>
                      <div>
                        <Label>Quantité</Label>
                        <Input 
                          type="number" 
                          step="any" 
                          value={cryptoForm.quantity} 
                          onChange={(e) => setCryptoForm({...cryptoForm, quantity: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="crypto-quantity-input"
                        />
                      </div>
                      <div>
                        <Label>Prix d'achat (EUR)</Label>
                        <Input 
                          type="number" 
                          step="any" 
                          value={cryptoForm.purchase_price} 
                          onChange={(e) => setCryptoForm({...cryptoForm, purchase_price: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="crypto-price-input"
                        />
                      </div>
                      <Button type="submit" className="w-full bg-white text-black hover:bg-gray-200" data-testid="crypto-submit-button">
                        Ajouter
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="space-y-3">
                {cryptos.length === 0 ? (
                  <div className="text-center text-[#A1A1AA] py-8">Aucune cryptomonnaie ajoutée</div>
                ) : (
                  cryptos.map((crypto) => {
                    const priceData = prices[`crypto-${crypto.id}`];
                    return (
                      <div 
                        key={crypto.id} 
                        className="flex justify-between items-center p-4 bg-[#09090B] border border-[#27272A] hover:border-[#3f3f46] transition-colors"
                        data-testid={`crypto-item-${crypto.symbol}`}
                      >
                        <div>
                          <div className="font-semibold text-[#FAFAFA]">{crypto.name}</div>
                          <div className="text-sm text-[#A1A1AA]">{crypto.symbol}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono text-[#FAFAFA]">
                            {priceData ? priceData.total_value_eur.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' }) : '...'}
                          </div>
                          <div className="text-sm text-[#A1A1AA]">{crypto.quantity} unités</div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleDelete('crypto', crypto.id)}
                          className="text-red-500 hover:text-red-400 hover:bg-red-900/20"
                          data-testid={`delete-crypto-${crypto.symbol}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>
          </TabsContent>

          {/* Stocks Tab */}
          <TabsContent value="stocks">
            <Card className="bg-[#18181B] border border-[#27272A] p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-['Chivo'] font-semibold">Actions</h2>
                <Dialog open={stockDialog} onOpenChange={setStockDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-white text-black hover:bg-gray-200" data-testid="add-stock-button">
                      <PlusCircle className="w-4 h-4 mr-2" />
                      Ajouter
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#18181B] border border-[#27272A] text-white">
                    <DialogHeader>
                      <DialogTitle>Ajouter une action</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddStock} className="space-y-4">
                      <div>
                        <Label>Nom</Label>
                        <Input 
                          value={stockForm.name} 
                          onChange={(e) => setStockForm({...stockForm, name: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="stock-name-input"
                        />
                      </div>
                      <div>
                        <Label>Symbole (ex: AAPL)</Label>
                        <Input 
                          value={stockForm.symbol} 
                          onChange={(e) => setStockForm({...stockForm, symbol: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="stock-symbol-input"
                        />
                      </div>
                      <div>
                        <Label>Quantité</Label>
                        <Input 
                          type="number" 
                          step="any" 
                          value={stockForm.quantity} 
                          onChange={(e) => setStockForm({...stockForm, quantity: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="stock-quantity-input"
                        />
                      </div>
                      <div>
                        <Label>Prix d'achat (EUR)</Label>
                        <Input 
                          type="number" 
                          step="any" 
                          value={stockForm.purchase_price} 
                          onChange={(e) => setStockForm({...stockForm, purchase_price: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="stock-price-input"
                        />
                      </div>
                      <Button type="submit" className="w-full bg-white text-black hover:bg-gray-200" data-testid="stock-submit-button">
                        Ajouter
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="space-y-3">
                {stocks.length === 0 ? (
                  <div className="text-center text-[#A1A1AA] py-8">Aucune action ajoutée</div>
                ) : (
                  stocks.map((stock) => {
                    const priceData = prices[`stock-${stock.id}`];
                    return (
                      <div 
                        key={stock.id} 
                        className="flex justify-between items-center p-4 bg-[#09090B] border border-[#27272A] hover:border-[#3f3f46] transition-colors"
                        data-testid={`stock-item-${stock.symbol}`}
                      >
                        <div>
                          <div className="font-semibold text-[#FAFAFA]">{stock.name}</div>
                          <div className="text-sm text-[#A1A1AA]">{stock.symbol}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono text-[#FAFAFA]">
                            {priceData ? priceData.total_value_eur.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' }) : '...'}
                          </div>
                          <div className="text-sm text-[#A1A1AA]">{stock.quantity} actions</div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleDelete('stocks', stock.id)}
                          className="text-red-500 hover:text-red-400 hover:bg-red-900/20"
                          data-testid={`delete-stock-${stock.symbol}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>
          </TabsContent>

          {/* Coins Tab */}
          <TabsContent value="coins">
            <Card className="bg-[#18181B] border border-[#27272A] p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-['Chivo'] font-semibold">Pièces de Monnaie</h2>
                <Dialog open={coinDialog} onOpenChange={setCoinDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-white text-black hover:bg-gray-200" data-testid="add-coin-button">
                      <PlusCircle className="w-4 h-4 mr-2" />
                      Ajouter
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#18181B] border border-[#27272A] text-white">
                    <DialogHeader>
                      <DialogTitle>Ajouter une pièce de monnaie</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddCoin} className="space-y-4">
                      <div>
                        <Label>Nom</Label>
                        <Input 
                          value={coinForm.name} 
                          onChange={(e) => setCoinForm({...coinForm, name: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="coin-name-input"
                        />
                      </div>
                      <div>
                        <Label>URL du site</Label>
                        <Input 
                          value={coinForm.url} 
                          onChange={(e) => setCoinForm({...coinForm, url: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          placeholder="https://example.com/price"
                          data-testid="coin-url-input"
                        />
                      </div>
                      <div>
                        <Label>Sélecteur CSS</Label>
                        <Input 
                          value={coinForm.css_selector} 
                          onChange={(e) => setCoinForm({...coinForm, css_selector: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          placeholder=".price-class"
                          data-testid="coin-selector-input"
                        />
                      </div>
                      <div>
                        <Label>Quantité</Label>
                        <Input 
                          type="number" 
                          step="any" 
                          value={coinForm.quantity} 
                          onChange={(e) => setCoinForm({...coinForm, quantity: e.target.value})} 
                          className="bg-[#09090B] border-[#27272A] text-white"
                          required
                          data-testid="coin-quantity-input"
                        />
                      </div>
                      <Button type="submit" className="w-full bg-white text-black hover:bg-gray-200" data-testid="coin-submit-button">
                        Ajouter
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="space-y-3">
                {coins.length === 0 ? (
                  <div className="text-center text-[#A1A1AA] py-8">Aucune pièce ajoutée</div>
                ) : (
                  coins.map((coin) => {
                    const priceData = prices[`coin-${coin.id}`];
                    return (
                      <div 
                        key={coin.id} 
                        className="flex justify-between items-center p-4 bg-[#09090B] border border-[#27272A] hover:border-[#3f3f46] transition-colors"
                        data-testid={`coin-item-${coin.name}`}
                      >
                        <div>
                          <div className="font-semibold text-[#FAFAFA]">{coin.name}</div>
                          <div className="text-xs text-[#A1A1AA] truncate max-w-xs">{coin.url}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono text-[#FAFAFA]">
                            {priceData ? priceData.total_value_eur.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' }) : '...'}
                          </div>
                          <div className="text-sm text-[#A1A1AA]">{coin.quantity} pièces</div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleDelete('coins', coin.id)}
                          className="text-red-500 hover:text-red-400 hover:bg-red-900/20"
                          data-testid={`delete-coin-${coin.name}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default Dashboard;