'use client';

import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function TradingChart({ data, type = 'candle', height = 400 }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px] text-gray-500">
        No data available
      </div>
    );
  }

  const labels = data.map(d => {
    const date = new Date(d.date || d.Date);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
  });

  const prices = data.map(d => d.close || d.Close || 0);
  const volumes = data.map(d => d.volume || d.Volume || 0);

  const priceChartData = {
    labels,
    datasets: [
      {
        label: 'Price',
        data: prices,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 6,
      },
    ],
  };

  const volumeChartData = {
    labels,
    datasets: [
      {
        label: 'Volume',
        data: volumes,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderRadius: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index',
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f3f4f6',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: (context) => `₹${context.parsed.y.toFixed(2)}`,
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(75, 85, 99, 0.1)',
        },
        ticks: {
          color: '#9ca3af',
          maxTicksLimit: 8,
        },
      },
      y: {
        grid: {
          color: 'rgba(75, 85, 99, 0.1)',
        },
        ticks: {
          color: '#9ca3af',
          callback: (value) => `₹${value}`,
        },
      },
    },
  };

  const volumeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f3f4f6',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 12,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
      },
    },
  };

  return (
    <div className="space-y-2">
      <div style={{ height: height - 100 }}>
        <Line data={priceChartData} options={chartOptions} />
      </div>
      <div style={{ height: 80 }}>
        <Bar data={volumeChartData} options={volumeOptions} />
      </div>
    </div>
  );
}
