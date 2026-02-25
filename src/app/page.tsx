"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { Search, Sparkles, ChevronDown, Loader2, MapPin } from "lucide-react";

interface Restaurant {
  id: number;
  name: string;
  image: string;
  rating: number;
  costForTwo: string;
  address: string;
  cuisines?: string;
  aiReason: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  // Filter States
  const [locations, setLocations] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);

  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState("");
  const [maxPrice, setMaxPrice] = useState("1000");
  const [minRating, setMinRating] = useState("4.0");

  useEffect(() => {
    // Fetch filter options on mount
    fetch("/api/locations")
      .then(res => res.json())
      .then(data => setLocations(data.locations || []))
      .catch(err => console.error(err));

    fetch("/api/cuisines")
      .then(res => res.json())
      .then(data => setCuisines(data.cuisines || []))
      .catch(err => console.error(err));
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const payload = {
        search_query: prompt || undefined,
        location: selectedLocation || undefined,
        cuisine: selectedCuisine || undefined,
        max_price: parseFloat(maxPrice),
        min_rating: parseFloat(minRating),
        top_n: 6
      };

      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.recommendation_text) {
        try {
          // Sync UI filters with AI-parsed values
          if (data.parsed_filters) {
            const pf = data.parsed_filters;
            if (pf.location) {
              const matchedLoc = locations.find(l => l.toLowerCase() === pf.location.toLowerCase()) ||
                locations.find(l => l.toLowerCase().includes(pf.location.toLowerCase()));
              setSelectedLocation(matchedLoc || pf.location);
            }
            if (pf.cuisine) {
              const matchedCui = cuisines.find(c => c.toLowerCase() === pf.cuisine.toLowerCase()) ||
                cuisines.find(c => c.toLowerCase().includes(pf.cuisine.toLowerCase()));
              setSelectedCuisine(matchedCui || pf.cuisine);
            }
            if (pf.max_price) setMaxPrice(pf.max_price.toString());

            // Rating Sync: If AI found a min_rating, use it. 
            // If AI found a max_rating (e.g. "under 4"), lower the dropdown to avoid conflict.
            if (pf.min_rating) {
              setMinRating(pf.min_rating.toFixed(1));
            } else if (pf.max_rating && pf.max_rating <= 4.0) {
              setMinRating("3.0"); // Lower the bar to show the "under 4" results
            }
          }

          // Groq returns JSON string
          const parsed = JSON.parse(data.recommendation_text);
          console.log("Parsed AI JSON:", parsed);

          // Deep check to prevent .map crashes (in case LLM wraps it weirdly)
          let restaurantList: Restaurant[] = [];
          if (Array.isArray(parsed.restaurants)) {
            restaurantList = parsed.restaurants;
          } else if (Array.isArray(parsed)) {
            restaurantList = parsed;
          } else if (parsed.restaurants && Array.isArray(parsed.restaurants.restaurants)) {
            // Edge case: Sometimes LLMs double-wrap {"restaurants": {"restaurants": []}}
            restaurantList = parsed.restaurants.restaurants;
          }

          setRestaurants(restaurantList);

          if (parsed.summary) {
            setSummary(parsed.summary);
          } else {
            setSummary("");
          }
        } catch (parseE) {
          console.error("Failed to parse JSON from AI string:", data.recommendation_text, parseE);
          setRestaurants([]); // Fallback to safe state
          setSummary("");
          alert("AI returned a malformed response. Please try again.");
        }
      }
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      alert("Error fetching from AI Backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 pb-20">

      {/* Header */}
      <header className="flex justify-between items-center py-4 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          {/* Logo - Text Based */}
          <h1 className="hidden md:block text-3xl font-black italic tracking-tighter text-[#E23744]">zomato</h1>

          {/* Location Pin - Primary on Mobile, Secondary on Desktop */}
          <div className="flex items-center gap-1 text-gray-700 font-medium md:border-l md:border-gray-300 md:pl-4 md:ml-2 cursor-pointer hover:text-rose-500 transition-colors">
            <div className="text-rose-500">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" /></svg>
            </div>
            <span className="text-sm">Bangalore</span>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors">
            <div className="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center overflow-hidden">
              <Image src="https://ui-avatars.com/api/?name=Sourabh+Sharma&background=FDA4AF&color=fff" alt="Profile" width={32} height={32} />
            </div>
            <span className="hidden md:block text-sm font-medium text-gray-700">Sourabh Sharma</span>
            <ChevronDown className="w-4 h-4 text-gray-400 hidden md:block" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 md:px-12 mt-6">

        {/* Beautiful AI Hero Section */}
        <section className="bg-gradient-to-br from-rose-400 to-rose-100 rounded-[2rem] p-6 md:p-12 mb-12 shadow-sm text-center">
          <h2 className="text-2xl md:text-4xl font-semibold mb-6 text-gray-900">
            Can&apos;t decide? Ask Zomato AI.
          </h2>

          <div className="max-w-3xl mx-auto bg-white rounded-full flex flex-col md:flex-row shadow-lg p-2 px-6 items-center mb-6 border border-gray-100">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder='Tell AI what you&apos;re craving... (e.g., "Spicy Thai in Koramangala under ₹1000 with great ambiance")'
              className="bg-transparent border-none outline-none w-full py-4 text-gray-700 text-sm md:text-base placeholder:text-gray-400"
            />
          </div>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            {/* Location Dropdown */}
            <div className="relative">
              <select
                className="appearance-none bg-white border text-sm md:text-base border-gray-200 rounded-full pl-4 pr-10 py-2 cursor-pointer hover:bg-gray-50 hover:shadow-sm transition-all focus:outline-none"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
              >
                <option value="">Select locality...</option>
                {locations.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
              <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-3 pointer-events-none" />
            </div>

            {/* Cuisine Dropdown */}
            <div className="relative">
              <select
                className="appearance-none bg-white border text-sm md:text-base border-gray-200 rounded-full pl-4 pr-10 py-2 cursor-pointer hover:bg-gray-50 hover:shadow-sm transition-all focus:outline-none"
                value={selectedCuisine}
                onChange={(e) => setSelectedCuisine(e.target.value)}
              >
                <option value="">Select cuisines...</option>
                {cuisines.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-3 pointer-events-none" />
            </div>

            {/* Price Dropdown */}
            <div className="relative">
              <select
                className="appearance-none bg-white border text-sm md:text-base border-gray-200 rounded-full pl-4 pr-10 py-2 cursor-pointer hover:bg-gray-50 hover:shadow-sm transition-all focus:outline-none"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              >
                <option value="500">Up to ₹500</option>
                <option value="1000">Up to ₹1000</option>
                <option value="2000">Up to ₹2000</option>
                <option value="5000">Up to ₹5000</option>
              </select>
              <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-3 pointer-events-none" />
            </div>

            {/* Rating Dropdown */}
            <div className="relative">
              <select
                className="appearance-none bg-white border text-sm md:text-base border-gray-200 rounded-full pl-4 pr-10 py-2 cursor-pointer hover:bg-gray-50 hover:shadow-sm transition-all focus:outline-none"
                value={minRating}
                onChange={(e) => setMinRating(e.target.value)}
              >
                <option value="3.0">3.0+ Stars</option>
                <option value="3.5">3.5+ Stars</option>
                <option value="4.0">4.0+ Stars</option>
                <option value="4.5">4.5+ Stars</option>
              </select>
              <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-3 pointer-events-none" />
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-[#E23744] hover:bg-[#Cb202d] text-white font-medium text-lg px-8 py-3 rounded-xl shadow-md transition-all active:scale-95 flex items-center justify-center mx-auto"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : "Get Recommendations"}
          </button>
        </section>

        {summary && (
          <section className="bg-rose-50 border border-rose-100 rounded-2xl p-6 md:p-8 mb-12 shadow-sm max-w-5xl mx-auto">
            <p className="text-sm md:text-base italic leading-relaxed text-center font-medium text-gray-800">
              {summary}
            </p>
          </section>
        )}

        {/* AI Recommendations Grid */}
        <section>
          {restaurants.length > 0 && <h3 className="text-xl md:text-2xl font-semibold mb-6 text-gray-900 flex items-center gap-2">Here you go. Problem solved.</h3>}

          {restaurants.length === 0 && !loading && (
            <div className="mt-20 text-left max-w-4xl">
              <h3 className="text-3xl font-bold text-gray-900 mb-4">Don’t overthink it. Just type it. 👀</h3>
              <p className="text-xl text-gray-600 leading-relaxed">
                The AI is ready for your wildest cravings. Be specific, be weird, we won’t judge.
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {restaurants.map((restaurant, idx) => (
              <div key={restaurant.id || idx} className="bg-white rounded-2xl shadow-[0_2px_12px_rgb(0,0,0,0.06)] border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow">
                {/* Content... */}
                <div className="p-4">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-semibold text-lg text-gray-900 truncate pr-2">{restaurant.name}</h4>
                  </div>

                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <svg key={star} className={`w-4 h-4 ${star <= Math.floor(restaurant.rating || 0) ? 'text-green-600 fill-green-600' : 'text-gray-300 fill-gray-300'}`} viewBox="0 0 24 24">
                          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      ))}
                    </div>
                    <span className="text-sm font-bold text-green-700">{restaurant.rating}</span>
                  </div>

                  {restaurant.cuisines && (
                    <div className="flex items-start gap-1.5 mb-2 text-gray-500 text-xs md:text-sm">
                      <span className="text-[#E23744] flex-shrink-0 mt-0.5">🍴</span>
                      <p className="leading-tight">{restaurant.cuisines}</p>
                    </div>
                  )}

                  <div className="flex items-start gap-1.5 mb-2 text-gray-500 text-xs md:text-sm">
                    <span className="text-[#E23744] flex-shrink-0 mt-0.5">💰</span>
                    <p className="leading-tight">Avg. ₹{restaurant.costForTwo} for two</p>
                  </div>

                  {restaurant.address && (
                    <div className="flex items-start gap-1.5 mb-4 text-gray-500 text-xs md:text-sm">
                      <MapPin className="w-4 h-4 text-[#E23744] flex-shrink-0 mt-0.5" />
                      <p className="leading-tight">{restaurant.address}</p>
                    </div>
                  )}

                  {/* AI Reason Block */}
                  <div className="bg-[#FFEBED] rounded-xl p-3 flex gap-3 items-start border border-rose-100">
                    <p className="text-xs lg:text-sm text-gray-800 leading-snug">
                      <span className="font-medium text-rose-600 mr-1">Why you&apos;ll like it:</span>
                      {restaurant.aiReason}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

      </main>
    </div>
  );
}
