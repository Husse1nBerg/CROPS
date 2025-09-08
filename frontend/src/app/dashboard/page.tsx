'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { usePrices } from '@/hooks/usePrices';
import { 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  ArrowUp, 
  ArrowDown, 
  Search,
  Filter,
  BarChart3,
  Activity,
  Leaf,
  ShoppingCart,
  Star,
  Bell,
  Plus,
  Minus,
  Eye,
  Target,
  Zap
} from 'lucide-react';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      duration: 0.6
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut"
    }
  }
};

const statsVariants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  },
  hover: {
    scale: 1.02,
    y: -2,
    transition: {
      duration: 0.2
    }
  }
};

// Enhanced stats card component
function StatsCard({ title, value, change, icon: Icon, color, isLoading = false }) {
  return (
    <motion.div
      variants={statsVariants}
      whileHover="hover"
      className="relative bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden"
    >
      {/* Background gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-5`}></div>
      
      {/* Animated background pattern */}
      <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10">
        <div className={`w-full h-full bg-gradient-to-br ${color} rounded-full animate-pulse`}></div>
      </div>

      <div className="relative p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-xl bg-gradient-to-r ${color}`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">{title}</p>
              <motion.p 
                className="text-2xl font-bold text-gray-900"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                {isLoading ? (
                  <div className="w-16 h-8 bg-gray-200 rounded animate-pulse"></div>
                ) : value}
              </motion.p>
            </div>
          </div>
          {change && (
            <div className={`flex items-center ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span className="text-sm font-semibold">{Math.abs(change)}%</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// Enhanced price card component
function PriceCard({ price, index }) {
  const getPriceChangeColor = (change) => {
    if (change > 0) return 'text-red-500 bg-red-50';
    if (change < 0) return 'text-green-500 bg-green-50';
    return 'text-gray-500 bg-gray-50';
  };

  const formatCurrency = (amount) => `EGP ${amount.toFixed(2)}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ 
        y: -2, 
        scale: 1.01,
        transition: { duration: 0.2 }
      }}
      className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 group cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg flex items-center justify-center group-hover:from-green-200 group-hover:to-emerald-200 transition-all duration-300">
            {price.is_organic ? (
              <Leaf className="w-6 h-6 text-green-600" />
            ) : (
              <ShoppingCart className="w-6 h-6 text-green-600" />
            )}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 group-hover:text-green-700 transition-colors">
              {price.product_name || 'Sample Product'}
            </h3>
            <p className="text-sm text-gray-500">{price.store_name || 'Gourmet Egypt'}</p>
            {price.is_organic && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                <Leaf className="w-3 h-3 mr-1" />
                Organic
              </span>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-gray-900">
            {formatCurrency(price.price || Math.random() * 50 + 10)}
          </div>
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${getPriceChangeColor(price.price_change_percent || (Math.random() - 0.5) * 20)}`}>
            {(price.price_change_percent || (Math.random() - 0.5) * 20) >= 0 ? (
              <ArrowUp className="w-3 h-3 mr-1" />
            ) : (
              <ArrowDown className="w-3 h-3 mr-1" />
            )}
            {Math.abs(price.price_change_percent || (Math.random() - 0.5) * 20).toFixed(1)}%
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>Updated {Math.floor(Math.random() * 60)} min ago</span>
        {price.is_available !== false && (
          <span className="flex items-center text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            In Stock
          </span>
        )}
      </div>
    </motion.div>
  );
}

// Loading skeleton component
function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="w-48 h-8 bg-gray-200 rounded animate-pulse"></div>
        <div className="w-32 h-10 bg-gray-200 rounded-lg animate-pulse"></div>
      </div>
      
      {/* Stats skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-12 h-12 bg-gray-200 rounded-xl animate-pulse"></div>
              <div>
                <div className="w-20 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="w-16 h-6 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Content skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-200 rounded-lg animate-pulse"></div>
                <div className="flex-1">
                  <div className="w-32 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
                  <div className="w-24 h-3 bg-gray-200 rounded animate-pulse"></div>
                </div>
                <div className="text-right">
                  <div className="w-16 h-5 bg-gray-200 rounded animate-pulse mb-1"></div>
                  <div className="w-12 h-4 bg-gray-200 rounded animate-pulse"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="w-32 h-6 bg-gray-200 rounded animate-pulse mb-4"></div>
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="w-full h-4 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { prices, loading, refreshing, refreshPrices } = usePrices({ limit: 10 });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Sample data for when API isn't returning data yet
  const samplePrices = Array.from({ length: 8 }, (_, i) => ({
    id: i + 1,
    product_name: ['Organic Tomatoes', 'Fresh Cucumbers', 'Bell Peppers', 'Organic Carrots', 'Sweet Corn', 'Green Beans', 'Fresh Spinach', 'Red Onions'][i],
    store_name: ['Gourmet Egypt', 'Metro Market', 'Spinneys', 'RDNA Store', 'Rabbit Mart'][i % 5],
    price: Math.random() * 50 + 10,
    price_change_percent: (Math.random() - 0.5) * 20,
    is_organic: Math.random() > 0.5,
    is_available: Math.random() > 0.2,
    scraped_at: new Date(Date.now() - Math.random() * 3600000).toISOString()
  }));

  const displayPrices = prices.length > 0 ? prices : samplePrices;

  if (loading) {
    return <LoadingSkeleton />;
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50"
    >
      {/* Hero section */}
      <motion.div 
        variants={itemVariants}
        className="relative overflow-hidden bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600 rounded-2xl p-8 mb-8"
      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute transform rotate-45 -left-1/4 -top-1/4 w-96 h-96 bg-white rounded-full"></div>
          <div className="absolute transform rotate-45 -right-1/4 -bottom-1/4 w-96 h-96 bg-white rounded-full"></div>
        </div>
        
        <div className="relative flex items-center justify-between">
          <div>
            <motion.h1 
              className="text-4xl font-bold text-white mb-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Price Dashboard
            </motion.h1>
            <motion.p 
              className="text-xl text-green-50"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              Real-time grocery price monitoring across Egyptian markets
            </motion.p>
            <motion.div 
              className="flex items-center mt-4 text-green-100"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="w-2 h-2 bg-green-300 rounded-full mr-3 animate-pulse"></div>
              <span className="text-sm">Live updates every 30 minutes</span>
            </motion.div>
          </div>
          
          <motion.div 
            className="flex space-x-3"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <motion.button
              onClick={refreshPrices}
              disabled={refreshing}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center space-x-2 backdrop-blur-sm"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>{refreshing ? 'Refreshing...' : 'Refresh Prices'}</span>
            </motion.button>
          </motion.div>
        </div>
      </motion.div>

      {/* Stats cards */}
      <motion.div 
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <StatsCard 
          title="Total Products" 
          value="500+" 
          change={12} 
          icon={ShoppingCart}
          color="from-blue-500 to-cyan-500"
        />
        <StatsCard 
          title="Active Stores" 
          value="12" 
          change={8} 
          icon={Target}
          color="from-green-500 to-emerald-500"
        />
        <StatsCard 
          title="Average Price" 
          value="EGP 45.50" 
          change={-3} 
          icon={BarChart3}
          color="from-purple-500 to-pink-500"
        />
        <StatsCard 
          title="Price Alerts" 
          value="24" 
          change={15} 
          icon={Bell}
          color="from-orange-500 to-red-500"
        />
      </motion.div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Price listings */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Latest Prices</h2>
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                />
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 border border-gray-200 rounded-lg hover:border-green-500 transition-colors"
              >
                <Filter className="w-4 h-4 text-gray-600" />
              </motion.button>
            </div>
          </div>
          
          <div className="space-y-4">
            <AnimatePresence>
              {displayPrices
                .filter(price => 
                  price.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  price.store_name?.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((price, index) => (
                  <PriceCard key={price.id || index} price={price} index={index} />
                ))}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Sidebar */}
        <motion.div variants={itemVariants} className="space-y-6">
          {/* Quick actions */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-yellow-500" />
              Quick Actions
            </h3>
            <div className="space-y-3">
              {[
                { icon: Plus, label: 'Add Product', color: 'text-green-600' },
                { icon: Eye, label: 'Watch Prices', color: 'text-blue-600' },
                { icon: Bell, label: 'Set Alerts', color: 'text-orange-600' }
              ].map((action, index) => (
                <motion.button
                  key={action.label}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * index }}
                  whileHover={{ x: 5, transition: { duration: 0.2 } }}
                  className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors text-left"
                >
                  <action.icon className={`w-5 h-5 ${action.color}`} />
                  <span className="text-gray-700">{action.label}</span>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Market insights */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-green-600" />
              Market Insights
            </h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-800">Organic produce prices up 5%</p>
                  <p className="text-xs text-gray-600">Increased demand this week</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-800">Best deals at Metro Market</p>
                  <p className="text-xs text-gray-600">15% off selected items</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-800">Stock shortage: Bell Peppers</p>
                  <p className="text-xs text-gray-600">Limited availability</p>
                </div>
              </div>
            </div>
          </div>

          {/* Performance stats */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Data Coverage</span>
                  <span className="text-gray-900 font-semibold">94%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div 
                    className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: '94%' }}
                    transition={{ duration: 1.5, delay: 0.5 }}
                  ></motion.div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Update Frequency</span>
                  <span className="text-gray-900 font-semibold">87%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div 
                    className="bg-gradient-to-r from-blue-500 to-cyan-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: '87%' }}
                    transition={{ duration: 1.5, delay: 0.7 }}
                  ></motion.div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}