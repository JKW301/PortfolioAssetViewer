import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { UserPlus, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import { API } from '../App';

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/signup`, {
        name: formData.name,
        email: formData.email,
        password: formData.password
      }, {
        withCredentials: true
      });

      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.detail || 'Une erreur est survenue lors de la création du compte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090B] flex items-center justify-center p-6">
      <Card className="bg-[#18181B] border border-[#27272A] p-8 md:p-12 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Chivo'] text-[#FAFAFA] mb-3">
            Créer un compte
          </h1>
          <p className="text-[#A1A1AA]">Rejoignez Portfolio Tracker</p>
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
            <Label htmlFor="name" className="text-[#FAFAFA]">Nom complet</Label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleChange}
              className="bg-[#27272A] border-[#3F3F46] text-[#FAFAFA] focus:border-white"
              placeholder="Votre nom complet"
            />
          </div>

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
                placeholder="Minimum 6 caractères"
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

          <div>
            <Label htmlFor="confirmPassword" className="text-[#FAFAFA]">Confirmer le mot de passe</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className="bg-[#27272A] border-[#3F3F46] text-[#FAFAFA] focus:border-white pr-10"
                placeholder="Confirmer votre mot de passe"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#A1A1AA] hover:text-[#FAFAFA]"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <Button 
            type="submit"
            disabled={loading}
            className="w-full bg-white text-black hover:bg-gray-200 font-semibold py-6 text-lg"
          >
            <UserPlus className="w-5 h-5 mr-2" />
            {loading ? 'Création...' : 'Créer mon compte'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-[#A1A1AA] text-sm">
            Déjà un compte ?{' '}
            <Link to="/login" className="text-white hover:underline">
              Se connecter
            </Link>
          </p>
        </div>

        <div className="mt-6 text-center text-sm text-[#A1A1AA]">
          <p>En créant un compte, vous acceptez nos conditions d'utilisation</p>
        </div>
      </Card>
    </div>
  );
}

export default Signup;