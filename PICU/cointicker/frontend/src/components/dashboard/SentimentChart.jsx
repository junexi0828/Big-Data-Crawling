import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import './SentimentChart.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const SentimentChart = ({ data }) => {
  if (!data || !data.timeline || data.timeline.length === 0) {
    return (
      <div className="chart-placeholder">
        감성 분석 데이터가 없습니다.
      </div>
    )
  }

  const chartData = {
    labels: data.timeline.map((item) => {
      const date = new Date(item.date)
      return date.toLocaleDateString('ko-KR', {
        month: 'short',
        day: 'numeric',
      })
    }),
    datasets: [
      {
        label: '긍정',
        data: data.timeline.map((item) => item.positive || 0),
        borderColor: '#43e97b',
        backgroundColor: 'rgba(67, 233, 123, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: '중립',
        data: data.timeline.map((item) => item.neutral || 0),
        borderColor: '#848e9c',
        backgroundColor: 'rgba(132, 142, 156, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: '부정',
        data: data.timeline.map((item) => item.negative || 0),
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#eaecef',
          usePointStyle: true,
          padding: 15,
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#1e2329',
        titleColor: '#eaecef',
        bodyColor: '#eaecef',
        borderColor: '#2b3139',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#848e9c',
        },
        grid: {
          color: '#2b3139',
        },
      },
      y: {
        ticks: {
          color: '#848e9c',
        },
        grid: {
          color: '#2b3139',
        },
      },
    },
  }

  return (
    <div className="sentiment-chart">
      <Line data={chartData} options={options} />
    </div>
  )
}

export default SentimentChart

