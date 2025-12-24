import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LogIn, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import { API } from '../App';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, {
          withCredentials: true
        });
        if (response.data) {
          navigate('/dashboard');
        }
      } catch (error) {
        // Not authenticated, show login
      }
    };
    checkAuth();
  }, [navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/login`, formData, {
        withCredentials: true
      });

      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.detail || 'Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090B] flex items-center justify-center p-6">
      <Card className="bg-[#18181B] border border-[#27272A] p-8 md:p-12 max-w-md w-full" data-testid="login-card">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Chivo'] text-[#FAFAFA] mb-3">
            Portfolio Tracker
          </h1>
          <p className="text-[#A1A1AA]">Connectez-vous pour accéder à votre portfolio</p>
        </div>

        {error && (
          <Alert className="mb-6 border-red-500/50 bg-red-500/10">
            <AlertDescription className="text-red-400">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email" className="text-[#FAFAFA]">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="bg-[#27272A] border-[#3F3F46] text-[#FAFAFA] focus:border-white"
              placeholder="votre@email.com"
            />
          </div>

          <div>
            <Label htmlFor="password" className="text-[#FAFAFA]">Mot de passe</Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                required
                value={formData.password}
                onChange={handleChange}
                className="bg-[#27272A] border-[#3F3F46] text-[#FAFAFA] focus:border-white pr-10"
                placeholder="Votre mot de passe"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#A1A1AA] hover:text-[#FAFAFA]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <Button 
            type="submit"
            disabled={loading}
            className="w-full bg-white text-black hover:bg-gray-200 font-semibold py-6 text-lg"
            data-testid="login-button"
          >
            <LogIn className="w-5 h-5 mr-2" />
            {loading ? 'Connexion...' : 'Se connecter'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-[#A1A1AA] text-sm">
            Pas encore de compte ?{' '}
            <Link to="/signup" className="text-white hover:underline">
              Créer un compte
            </Link>
          </p>
        </div>

        <div className="mt-6 text-center text-sm text-[#A1A1AA]">
          <p>En vous connectant, vous acceptez nos conditions d'utilisation</p>
        </div>
      </Card>
    </div>
  );
}

export default Login;

export default Login;