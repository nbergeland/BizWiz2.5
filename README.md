# 🍗 BizWiz2.5: Dynamic Analytics

**Real-Time Location Intelligence for Restaurant Market Analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Plotly](https://img.shields.io/badge/Built%20with-Plotly-brightgreen)](https://plotly.com/)

BizWiz is a sophisticated business intelligence platform designed specifically for restaurant location analysis and market research. It combines real-time data collection, machine learning predictions, and interactive visualizations to help restaurant chains identify optimal expansion locations.

## 🌟 Key Features

### 📊 Real-Time Data Integration
- **Census API Integration**: Live demographic data collection
- **Google Places API**: Real competitor location mapping
- **Dynamic Traffic Analysis**: Location accessibility scoring
- **Commercial Intelligence**: Zoning and business density analysis

### 🤖 Advanced Analytics
- **Machine Learning Models**: Revenue prediction based on 15+ factors
- **Competition Analysis**: Distance-based cannibalization modeling
- **Market Segmentation**: Income, age, and traffic pattern analysis
- **Performance Metrics**: R² scoring and cross-validation

### 🗺️ Interactive Dashboard
- **Live Location Maps**: Real-time competitor and opportunity visualization
- **Revenue Heatmaps**: Color-coded potential analysis
- **Opportunity Ranking**: Top 20 location recommendations
- **Model Intelligence**: Feature importance and prediction insights

### 🏗️ Scalable Architecture
- **Multi-City Support**: Configurable city boundaries and parameters
- **Async Processing**: Efficient data loading and API management
- **Smart Caching**: 1-hour cache with force refresh options
- **Progress Tracking**: Real-time loading status and ETA

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Places API key (optional but recommended)
- Census API key (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/bizwiz-dynamic-analytics.git
cd bizwiz-dynamic-analytics
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys** (optional)
```python
# In dynamic_data_loader.py, update:
self.google_places_api_key = "YOUR_GOOGLE_PLACES_API_KEY"
self.census_api_key = "YOUR_CENSUS_API_KEY"
```

4. **Launch the dashboard**
```bash
python launch_dynamic_dashboard.py
```

5. **Open your browser**
Navigate to `http://127.0.0.1:8051`

## 📋 Requirements

```txt
dash>=2.14.0
dash-bootstrap-components>=1.4.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
aiohttp>=3.8.0
requests>=2.31.0
```

## 🛠️ Configuration

### City Configuration

The system supports multiple cities through the `CityConfigManager`. Each city requires:

```python
@dataclass
class CityConfiguration:
    city_id: str
    display_name: str
    bounds: GeographicBounds
    demographics: DemographicProfile
    competitor_data: CompetitorConfiguration
    market_data: MarketData
```

### API Configuration

#### Google Places API (Recommended)
- Enables real competitor location discovery
- Provides business ratings and review data
- Required for accurate competition analysis

#### Census API (Optional)
- Provides official demographic data
- Fallback to synthetic data if unavailable
- Enhances income and population accuracy

## 📊 Usage Examples

### Basic City Analysis

```python
from dynamic_data_loader import load_city_data_on_demand

# Load data for a city
city_data = await load_city_data_on_demand(
    city_id="grand_forks_nd",
    force_refresh=True
)

# Access results
df = city_data['df_filtered']
competitors = city_data['competitor_data']
metrics = city_data['metrics']

print(f"Analyzed {len(df)} locations")
print(f"Revenue range: ${df['predicted_revenue'].min():,.0f} - ${df['predicted_revenue'].max():,.0f}")
```

### Custom Progress Tracking

```python
def progress_callback(progress):
    print(f"[{progress.city_id}] {progress.step_name} - "
          f"{progress.progress_percent:.1f}% complete")

city_data = await load_city_data_on_demand(
    city_id="target_city", 
    progress_callback=progress_callback
)
```

## 🏗️ Architecture

### Core Components

1. **Dynamic Data Loader** (`dynamic_data_loader.py`)
   - Async API integration
   - Data processing and feature engineering
   - Machine learning model training

2. **Dashboard Interface** (`dynamic_dashboard.py`)
   - Real-time UI updates
   - Interactive maps and charts
   - Progress tracking and error handling

3. **City Configuration** (`city_config.py`)
   - Geographic boundary definitions
   - Market-specific parameters
   - Competitor search terms

### Data Flow

```
📡 API Sources → 🔄 Data Loader → 🤖 ML Model → 📊 Dashboard
     ↓              ↓              ↓           ↓
  Census API    Feature Eng    Revenue Pred   Live UI
  Places API    Competitor     Performance    Maps/Charts
  Traffic Data  Analysis       Metrics        Ranking
```

## 🧪 Model Performance

### Revenue Prediction Model

- **Algorithm**: Random Forest Regressor (150 trees)
- **Features**: 15+ engineered features including:
  - Demographics (income, age, population)
  - Traffic patterns and accessibility
  - Competition distance and density
  - Commercial viability scores
  - Location-specific interactions

- **Performance Metrics**:
  - R² Score: Typically 0.85-0.95
  - Cross-validation MAE: ~$400k
  - Revenue Range: $2.8M - $9.2M (realistic for fast-casual)

### Feature Engineering

```python
# Key engineered features
distance_from_center = sqrt((lat - center_lat)² + (lon - center_lon)²) * 69
income_age_interaction = median_income * median_age
traffic_commercial_interaction = traffic_score * commercial_score
competition_pressure = competition_density / (distance_to_competitor + 0.1)
```

## 🎯 Use Cases

### Restaurant Chain Expansion
- Identify optimal locations for new restaurants
- Analyze market saturation and competition
- Predict revenue potential for specific sites

### Market Research
- Understand demographic trends in target markets
- Compare market opportunities across cities
- Analyze competitor distribution patterns

### Investment Analysis
- Evaluate real estate opportunities
- Assess market risk and potential returns
- Support franchise location decisions

## 🔧 Customization

### Adding New Cities

1. Create city configuration in `city_config.py`
2. Define geographic bounds and market parameters
3. Add competitor search terms
4. Update city selector in dashboard

### Model Tuning

```python
# Adjust model parameters in _train_revenue_model()
model = RandomForestRegressor(
    n_estimators=200,     # Increase for better accuracy
    max_depth=15,         # Adjust based on overfitting
    random_state=42,      # Keep consistent for reproducibility
    min_samples_split=3   # Tune for your data size
)
```

### Custom Scoring

```python
# Modify revenue calculation in _train_revenue_model()
base_revenue = 4_200_000  # Adjust for your restaurant type
income_impact_factor = 0.3  # Tune demographic importance
traffic_impact_factor = 0.4  # Adjust traffic weighting
```

## 🚨 Troubleshooting

### Common Issues

**API Rate Limits**
```python
# Increase delays between API calls
await asyncio.sleep(0.5)  # Increase from 0.1
```

**Memory Issues with Large Cities**
```python
# Reduce grid density
adaptive_spacing = max(adaptive_spacing, 0.005)  # Increase minimum spacing
```

**Model Performance Issues**
```python
# Add more validation
if y.std() < 200_000:
    logger.warning("Low revenue variance detected")
    # Add additional variance factors
```

### Debugging Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Optimization

### For Large Cities
- Implement batch processing for grid points
- Use async/await for concurrent API calls
- Cache intermediate results aggressively

### For Production Use
- Implement Redis for distributed caching
- Add database storage for historical data
- Set up API rate limiting and quotas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for public methods
- Add unit tests for core functionality
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Plotly & Dash**: For the excellent visualization framework
- **Scikit-learn**: For machine learning capabilities
- **Google Places API**: For real competitor data
- **US Census Bureau**: For demographic data access

## 🗺️ Future Roadmap

BizWiz is evolving from a restaurant-focused platform into a comprehensive **multi-industry location intelligence suite**. Our vision is to become the go-to solution for data-driven site selection across various retail and service sectors.

### 🎯 Planned Industry Expansions

#### 🍟 Quick Service Restaurant (QSR) Enhancement
**Timeline: Q2 2024**
- **Drive-thru optimization**: Traffic flow analysis and queue management modeling
- **Speed of service metrics**: Integration with POS systems for performance tracking
- **Menu-specific modeling**: Revenue predictions based on menu categories and price points
- **Franchise-specific parameters**: Customizable models for different QSR brands
- **Peak hour analysis**: Time-based demand forecasting and staffing optimization

#### 🏦 Banking & Financial Services
**Timeline: Q3-Q4 2024**
- **ATM placement optimization**: Cash demand modeling and accessibility analysis
- **Branch location analysis**: Population density and banking behavior patterns
- **Competition mapping**: Existing bank locations and market saturation analysis
- **Regulatory compliance**: Zoning restrictions and CRA (Community Reinvestment Act) considerations
- **Demographic targeting**: Age and income-based service demand prediction
- **Mobile banking impact**: Digital adoption rates affecting physical location needs

#### ⛽ Gas Station & Convenience Store
**Timeline: Q1 2025**
- **Traffic flow modeling**: Vehicle count analysis and commuter pattern recognition
- **Fuel demand forecasting**: Local consumption patterns and price sensitivity analysis
- **Competition analysis**: Existing stations, pricing strategies, and brand loyalty factors
- **Convenience store optimization**: Product mix recommendations based on local demographics
- **EV charging integration**: Electric vehicle adoption rates and charging infrastructure needs
- **Highway vs. urban analysis**: Different modeling approaches for highway vs. city locations

### 🚀 Platform Enhancements

#### 📊 Advanced Analytics Engine
- **Multi-industry modeling**: Configurable algorithms for different business types
- **Comparative analysis**: Cross-industry performance benchmarking
- **Risk assessment**: Market volatility and economic impact modeling
- **ROI calculators**: Industry-specific return on investment projections

#### 🛠️ Enterprise Features
- **Multi-tenant architecture**: Support for multiple brands/franchisees
- **API marketplace**: Third-party integrations for specialized data sources
- **White-label solutions**: Customizable branding for consulting firms
- **Advanced reporting**: Executive dashboards and automated insights

#### 🌐 Data Integration Expansions
- **Satellite imagery analysis**: Parking availability and building footprint analysis
- **Mobile location data**: Foot traffic patterns and customer journey mapping
- **Social media sentiment**: Local market perception and brand awareness
- **Economic indicators**: Regional economic health and growth projections

### 🏗️ Technical Roadmap

#### Phase 1: Multi-Industry Framework (2024)
```python
class IndustryConfigManager:
    supported_industries = [
        'fast_casual_restaurant',
        'quick_service_restaurant', 
        'banking_branch',
        'atm_location',
        'gas_station',
        'convenience_store'
    ]
```

#### Phase 2: Specialized Models (2024-2025)
- Industry-specific feature engineering
- Custom revenue/performance prediction models
- Regulatory and compliance integration
- Specialized competitor analysis

#### Phase 3: Enterprise Platform (2025+)
- Multi-tenant SaaS architecture
- Advanced API ecosystem
- Real-time data streaming
- AI-powered insights and recommendations

### 💡 Innovation Pipeline

#### Emerging Technologies
- **Computer Vision**: Automated site assessment from street view imagery
- **IoT Integration**: Real-time foot traffic and environmental data
- **Blockchain**: Secure data sharing between franchisees and corporate
- **Edge Computing**: Local processing for real-time decision making

#### Research & Development
- **Predictive maintenance**: Equipment failure prediction for gas stations/banks
- **Dynamic pricing models**: Real-time pricing optimization based on demand
- **Sustainability metrics**: Environmental impact assessment for site selection
- **Autonomous vehicle impact**: Future-proofing location strategies for AV adoption

### 🤝 Partnership Opportunities

We're actively seeking partnerships with:
- **Industry associations**: QSR chains, banking institutions, fuel retailers
- **Data providers**: Traffic analytics, demographic research, commercial real estate
- **Technology vendors**: POS systems, IoT sensors, mapping services
- **Consulting firms**: Site selection specialists and market research companies

### 📈 Market Impact Goals

By 2026, we aim to:
- **500+ enterprise clients** across multiple industries
- **10,000+ locations analyzed** monthly through the platform
- **$2B+ in site selection decisions** influenced by BizWiz analytics
- **25+ integrations** with industry-standard data sources and systems

---

## 📞 Support

For questions, issues, or feature requests:

- 📧 Email: support@bizwiz-analytics.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/bizwiz-dynamic-analytics/issues)
- 📖 Docs: [Full Documentation](https://your-docs-site.com)
- 🤝 Partnerships: partnerships@bizwiz-analytics.com

---

**Built with ❤️ for data-driven site selection across industries**

*BizWiz is transforming how businesses make location decisions through real-time market intelligence, predictive analytics, and industry-specific insights.*
