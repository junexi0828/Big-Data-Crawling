<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>동아리 관리 플랫폼 재무 시뮬레이션</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-annotation/2.1.0/chartjs-plugin-annotation.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2em;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .summary-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metric-card {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .warning { color: #f39c12; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>올인원 동아리 관리 플랫폼 재무 시뮬레이션</h1>

        <div class="summary-box">
            <h2 style="color: white; border: none; margin-top: 0;">핵심 재무 지표</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">₩1,064,000</div>
                    <div class="metric-label">초기 투자금</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">₩2,218,000</div>
                    <div class="metric-label">월간 운영비</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">15개월</div>
                    <div class="metric-label">예상 손익분기점</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">₩75,000,000</div>
                    <div class="metric-label">3년차 연간 목표 수익</div>
                </div>
            </div>
        </div>

        <h2>📊 월별 수익 구성</h2>
        <div class="chart-container">
            <canvas id="revenueChart"></canvas>
        </div>

        <div class="grid">
            <div>
                <h2>💰 수익 vs 지출</h2>
                <div class="chart-container">
                    <canvas id="profitChart"></canvas>
                </div>
            </div>
            <div>
                <h2>📈 누적 현금 흐름</h2>
                <div class="chart-container">
                    <canvas id="cashFlowChart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid">
            <div>
                <h2>👥 사용자 증가</h2>
                <div class="chart-container">
                    <canvas id="usersChart"></canvas>
                </div>
            </div>
            <div>
                <h2>🔍 비용 구성</h2>
                <div class="chart-container">
                    <canvas id="costBreakdownChart"></canvas>
                </div>
            </div>
        </div>

        <h2>📋 시나리오별 분석</h2>
        <table>
            <thead>
                <tr>
                    <th>시나리오</th>
                    <th>3년 후 누적 현금</th>
                    <th>손익분기점</th>
                    <th>연간 수익 (3년차)</th>
                    <th>위험도</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>보수적</td>
                    <td class="negative">₩-15,000,000</td>
                    <td>미달성</td>
                    <td>₩52,500,000</td>
                    <td class="negative">높음</td>
                </tr>
                <tr>
                    <td>기본</td>
                    <td class="positive">₩25,000,000</td>
                    <td>15개월</td>
                    <td>₩75,000,000</td>
                    <td class="warning">중간</td>
                </tr>
                <tr>
                    <td>낙관적</td>
                    <td class="positive">₩65,000,000</td>
                    <td>12개월</td>
                    <td>₩90,000,000</td>
                    <td class="positive">낮음</td>
                </tr>
            </tbody>
        </table>

        <h2>⚠️ 리스크 분석 및 권장사항</h2>
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #856404; margin-top: 0;">주요 리스크</h3>
            <ul>
                <li><strong>초기 현금 부족:</strong> 첫 12개월간 약 ₩20,000,000의 현금 부족 예상</li>
                <li><strong>사용자 확보 지연:</strong> 1단계 사용자 증가율이 목표에 미달할 경우</li>
                <li><strong>B2B/B2G 전환 실패:</strong> 2단계 수익 모델 실현이 지연될 경우</li>
            </ul>

            <h3 style="color: #856404;">권장사항</h3>
            <ul>
                <li><strong>초기 자본:</strong> 최소 ₩35,000,000 확보 (안전 마진 포함)</li>
                <li><strong>마일스톤 관리:</strong> 6개월마다 사용자 증가율 및 수익 모델 재검토</li>
                <li><strong>비용 최적화:</strong> 초기 마케팅 비용을 성과 기반으로 조정</li>
                <li><strong>파트너십:</strong> 대학 및 기업과의 조기 파트너십 구축</li>
            </ul>
        </div>
    </div>

    <script>
        // 월별 데이터 생성
        const months = Array.from({length: 36}, (_, i) => i + 1);

        // 수익 데이터 계산
        function calculateRevenue() {
            const data = {
                phase1: [],
                b2b: [],
                b2g: [],
                total: [],
                users: [],
                expenses: [],
                cumulative: []
            };

            let cumulativeCash = -1064000; // 초기 투자

            for (let month = 1; month <= 36; month++) {
                // 1단계 광고 수익 (1-12월)
                let phase1Revenue = 0;
                let users = 0;
                if (month <= 12) {
                    users = Math.min(100 * Math.pow(1.15, month - 1), 5000);
                    phase1Revenue = users * 3000;
                } else {
                    users = 6000; // 2단계에서 사용자 유지
                }

                // 2단계 수익 (13월부터)
                let b2bRevenue = 0;
                let b2gRevenue = 0;
                if (month >= 13) {
                    const monthsFrom13 = month - 13;
                    b2bRevenue = (50000000 / 12) * Math.pow(1.1, monthsFrom13 / 12);
                    b2gRevenue = (25000000 / 12) * Math.pow(1.08, monthsFrom13 / 12);
                }

                const totalRevenue = phase1Revenue + b2bRevenue + b2gRevenue;

                // 지출 계산
                let monthlyExpense = 2218000;
                if (month > 6) {
                    monthlyExpense *= (1 + 0.05 * Math.floor((month - 1) / 6));
                }

                cumulativeCash += (totalRevenue - monthlyExpense);

                data.phase1.push(phase1Revenue / 1000000);
                data.b2b.push(b2bRevenue / 1000000);
                data.b2g.push(b2gRevenue / 1000000);
                data.total.push(totalRevenue / 1000000);
                data.users.push(Math.round(users));
                data.expenses.push(monthlyExpense / 1000000);
                data.cumulative.push(cumulativeCash / 1000000);
            }

            return data;
        }

        const revenueData = calculateRevenue();

        // 차트 1: 월별 수익 구성
        new Chart(document.getElementById('revenueChart'), {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: '1단계 광고 수익',
                        data: revenueData.phase1,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: false
                    },
                    {
                        label: 'B2B 수익',
                        data: revenueData.b2b,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        fill: false
                    },
                    {
                        label: 'B2G 수익',
                        data: revenueData.b2g,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        fill: false
                    },
                    {
                        label: '총 수익',
                        data: revenueData.total,
                        borderColor: '#9b59b6',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        borderWidth: 3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '수익 (백만원)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '월'
                        }
                    }
                }
            }
        });

        // 차트 2: 수익 vs 지출
        new Chart(document.getElementById('profitChart'), {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: '총 수익',
                        data: revenueData.total,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        fill: false
                    },
                    {
                        label: '월간 지출',
                        data: revenueData.expenses,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.2)',
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '금액 (백만원)'
                        }
                    }
                }
            }
        });

        // 차트 3: 누적 현금 흐름
        new Chart(document.getElementById('cashFlowChart'), {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: '누적 현금',
                    data: revenueData.cumulative,
                    borderColor: '#3498db',
                    backgroundColor: function(context) {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgba(46, 204, 113, 0.3)' : 'rgba(231, 76, 60, 0.3)';
                    },
                    fill: true,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: '누적 현금 (백만원)'
                        }
                    }
                },
                plugins: {
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                yMin: 0,
                                yMax: 0,
                                borderColor: 'red',
                                borderWidth: 2,
                                borderDash: [5, 5]
                            }
                        }
                    }
                }
            }
        });

        // 차트 4: 사용자 증가
        new Chart(document.getElementById('usersChart'), {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: '활성 사용자 수',
                    data: revenueData.users,
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.2)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '사용자 수'
                        }
                    }
                }
            }
        });

        // 차트 5: 비용 구성 (파이 차트)
        new Chart(document.getElementById('costBreakdownChart'), {
            type: 'doughnut',
            data: {
                labels: ['인건비', '서버/클라우드', '마케팅', 'SaaS', '기타'],
                datasets: [{
                    data: [1500000, 230000, 350000, 80000, 58000],
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#e74c3c',
                        '#f39c12',
                        '#9b59b6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>