import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LogIn } from 'lucide-react';
import axios from 'axios';
import { API } from '../App';

function Login() {
  const navigate = useNavigate();

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

  const handleGoogleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
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

        <Button 
          onClick={handleGoogleLogin}
          className="w-full bg-white text-black hover:bg-gray-200 font-semibold py-6 text-lg"
          data-testid="google-login-button"
        >
          <LogIn className="w-5 h-5 mr-2" />
          Se connecter avec Google
        </Button>

        <div className="mt-6 text-center text-sm text-[#A1A1AA]">
          <p>En vous connectant, vous acceptez nos conditions d'utilisation</p>
        </div>
      </Card>
    </div>
  );
}

export default Login;