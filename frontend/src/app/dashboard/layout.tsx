
// Protected layout for dashboard pages

'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Loader2, 
  Home, 
  BarChart3, 
  ShoppingCart, 
  Store, 
  Settings, 
  LogOut, 
  Leaf,
  Bell,
  User,
  Search,
  Menu,
  X
} from 'lucide-react';
import axios from 'axios';
import Link from 'next/link';

const navigationItems = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Prices', href: '/dashboard/prices', icon: BarChart3 },
  { name: 'Products', href: '/dashboard/products', icon: ShoppingCart },
  { name: 'Stores', href: '/dashboard/stores', icon: Store },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

function Sidebar({ isOpen, onClose }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    localStorage.removeItem('token');
    router.push('/auth/login');
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose}></div>
      )}
      
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ x: isOpen ? 0 : '-100%' }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 h-full w-64 bg-white shadow-xl z-50 lg:relative lg:translate-x-0 lg:shadow-none lg:border-r lg:border-gray-200"
      >
        {/* Header with enhanced styling */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg blur-lg opacity-70 group-hover:opacity-90 transition-opacity"></div>
              <div className="relative bg-gradient-to-r from-green-500 to-emerald-600 p-2.5 rounded-lg">
                <Leaf className="w-7 h-7 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                CROPS
              </h1>
              <p className="text-xs text-gray-500">Dashboard</p>
            </div>
          </Link>
          <motion.button 
            onClick={onClose} 
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <X className="w-6 h-6 text-gray-500" />
          </motion.button>
        </div>

        {/* Navigation with enhanced styling */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navigationItems.map((item, index) => {
              const isActive = pathname === item.href;
              return (
                <motion.li 
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Link
                    href={item.href}
                    className={`group flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                      isActive
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-200'
                        : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 hover:text-green-700'
                    }`}
                    onClick={() => onClose()}
                  >
                    <div className={`p-1.5 rounded-lg transition-all ${
                      isActive 
                        ? 'bg-white/20' 
                        : 'group-hover:bg-green-100'
                    }`}>
                      <item.icon className="w-5 h-5" />
                    </div>
                    <span className="font-semibold">{item.name}</span>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="ml-auto w-2 h-2 bg-white rounded-full"
                        initial={false}
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Link>
                </motion.li>
              );
            })}
          </ul>
        </nav>

        {/* Footer with enhanced logout */}
        <div className="p-4 border-t border-gray-200/50">
          <motion.button
            onClick={handleLogout}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="group flex items-center space-x-3 w-full px-4 py-3 text-red-600 hover:bg-gradient-to-r hover:from-red-50 hover:to-red-100 rounded-xl transition-all duration-300"
          >
            <div className="p-1.5 rounded-lg group-hover:bg-red-100 transition-all">
              <LogOut className="w-5 h-5" />
            </div>
            <span className="font-semibold">Logout</span>
          </motion.button>
        </div>
      </motion.aside>
    </>
  );
}

function Header({ onMenuClick }) {
  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
          
          {/* Search bar with homepage styling */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search products, stores..."
              className="pl-10 pr-4 py-3 w-64 lg:w-80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
            />
          </div>
        </div>

        <div className="flex items-center space-x-3 sm:space-x-4">
          {/* Notifications with enhanced styling */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-3 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-xl transition-all"
          >
            <Bell className="w-5 h-5" />
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center shadow-lg"
            >
              <span className="text-xs text-white font-semibold">3</span>
            </motion.div>
          </motion.button>

          {/* Profile with enhanced styling */}
          <motion.div 
            whileHover={{ scale: 1.02 }}
            className="flex items-center space-x-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-green-50 hover:to-emerald-50 rounded-xl p-2 transition-all cursor-pointer"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full blur-sm opacity-70"></div>
              <div className="relative w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-semibold text-gray-900">Test User</p>
              <p className="text-xs text-gray-500">Administrator</p>
            </div>
          </motion.div>
        </div>
      </div>
    </header>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/auth/login');
        return;
      }

      // Verify token with backend via Next.js API route
      const response = await axios.get('/api/auth/session', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.valid) {
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('token');
        router.push('/auth/login');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      router.push('/auth/login');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-gray-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full blur-lg opacity-70"></div>
            <div className="relative bg-gradient-to-r from-green-500 to-emerald-600 p-4 rounded-full">
              <Leaf className="w-8 h-8 text-white animate-pulse" />
            </div>
          </div>
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-2" />
          <p className="text-gray-600 font-medium">Loading your dashboard...</p>
        </motion.div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Background Elements for consistency with homepage */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-10 w-72 h-72 bg-green-200 rounded-full blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute bottom-20 left-10 w-96 h-96 bg-emerald-200 rounded-full blur-3xl opacity-30 animate-pulse"></div>
      </div>
      
      <div className="flex h-screen relative">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header onMenuClick={() => setSidebarOpen(true)} />
          
          <main className="flex-1 overflow-y-auto">
            <div className="p-4 sm:p-6 lg:p-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="relative"
              >
                {children}
              </motion.div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
