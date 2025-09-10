# 🌱 EcoLearning Platform

A gamified environmental education platform that makes learning engaging and action-driven through interactive quizzes, real-world eco-tasks, and a comprehensive reward system.

## ✨ Features

### 🎮 Gamified Learning
- **Interactive Quizzes**: Environmental education quizzes with immediate feedback
- **Eco-Token Rewards**: Earn tokens for completing activities and achieving milestones
- **Level System**: Progress through levels based on experience points
- **Achievement System**: Unlock badges and achievements for various accomplishments

### 🌍 Real-World Impact
- **Eco-Tasks**: Complete real-world environmental activities in your community
- **Photo/Video Verification**: Document your environmental impact
- **Community Challenges**: Participate in group challenges and competitions
- **Impact Tracking**: Monitor your environmental contributions

### 🏆 Competition & Social Features
- **Multi-Level Leaderboards**: Compete locally (school, city) and globally
- **Seasonal Competitions**: Special themed challenges throughout the year
- **Peer Comparison**: See how you rank among classmates and friends
- **Social Sharing**: Share achievements and progress

### 🎁 Reward System
- **Token Economy**: Comprehensive eco-token system with earning and spending mechanics
- **Reward Store**: Redeem tokens for discounts, merchandise, and environmental donations
- **Daily Limits**: Prevent token farming with smart daily earning limits
- **Bonus Multipliers**: Streak bonuses and level-based multipliers

### 🤖 AI Support
- **EcoBot Chatbot**: AI assistant for learning support and platform guidance
- **Personalized Recommendations**: Get quiz and task suggestions based on your progress
- **Environmental Facts**: Learn interesting eco-facts through conversations
- **Progress Insights**: Get detailed analytics on your learning journey

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone or download the project**
   ```bash
   cd "c:\Users\hp\Desktop\project 1 django"
   ```

2. **Activate virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py loaddata sample_data.json
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📱 Application Structure

### Core Apps

- **accounts**: User authentication, profiles, and gamification features
- **quizzes**: Interactive quiz system with categories and scoring
- **eco_tasks**: Real-world environmental task management
- **rewards**: Eco-token system and reward store
- **leaderboards**: Multi-level ranking and competition system
- **chatbot**: AI-powered learning assistant
- **api**: REST API endpoints for mobile/external integrations

### Key Models

#### User & Gamification
- `User`: Extended user model with gamification fields
- `UserProfile`: Additional profile information and statistics
- `Achievement`: System achievements and badges
- `UserAchievement`: User-earned achievements tracking

#### Learning System
- `Quiz`: Environmental education quizzes
- `Question`: Quiz questions with multiple choice answers
- `QuizAttempt`: User quiz attempts and scoring
- `EcoTask`: Real-world environmental tasks
- `UserTask`: User task progress and submissions

#### Rewards & Competition
- `EcoTokenTransaction`: Complete token transaction history
- `RewardItem`: Available rewards in the token store
- `LeaderboardEntry`: User rankings across different scopes
- `LeaderboardSeason`: Seasonal competitions and events

## 🎯 Usage Guide

### For Students

1. **Getting Started**
   - Register with your school information
   - Complete your profile setup
   - Take the welcome quiz to earn your first tokens

2. **Learning Path**
   - Browse quiz categories (Climate Change, Biodiversity, etc.)
   - Complete quizzes to earn eco-tokens and experience
   - Aim for perfect scores to get bonus rewards

3. **Taking Action**
   - Explore available eco-tasks in your area
   - Complete real-world environmental activities
   - Submit photos/videos as verification
   - Earn tokens and make a real impact

4. **Competition**
   - Check leaderboards to see your ranking
   - Compete with classmates and global users
   - Join seasonal challenges for extra rewards

5. **Rewards**
   - Visit the reward store to spend your tokens
   - Redeem discounts, badges, or make environmental donations
   - Track your reward history

### For Educators

1. **Content Management**
   - Access the admin panel to create quizzes and tasks
   - Set up school-specific challenges
   - Monitor student progress and engagement

2. **Classroom Integration**
   - Use leaderboards to encourage healthy competition
   - Assign specific eco-tasks as homework
   - Track class performance through analytics

## 🔧 Configuration

### Environment Variables
```
SECRET_KEY=your-django-secret-key
DEBUG=True/False
DATABASE_URL=your-database-url (optional)
```

### Customization Options

- **Token Earning Rules**: Modify `TokenEarningRule` to adjust reward amounts
- **Achievement System**: Add new achievements through the admin panel
- **Quiz Categories**: Create custom categories for your curriculum
- **Task Templates**: Set up reusable task templates for common activities

## 📊 Analytics & Monitoring

The platform includes comprehensive analytics:

- **User Progress Tracking**: Individual learning journeys
- **Engagement Metrics**: Quiz completion rates, task participation
- **Token Economy Health**: Earning vs. spending patterns
- **Leaderboard Analytics**: Competition participation and rankings
- **Chatbot Performance**: Conversation success rates and user satisfaction

## 🔒 Security Features

- **User Authentication**: Secure login/logout with session management
- **Permission System**: Role-based access control
- **Data Validation**: Input sanitization and validation
- **CSRF Protection**: Cross-site request forgery prevention
- **Rate Limiting**: API rate limiting for abuse prevention

## 🌐 API Documentation

RESTful API endpoints available at `/api/`:

- `GET /api/users/` - User information
- `GET /api/quizzes/` - Available quizzes
- `GET /api/tasks/` - Available eco-tasks
- `GET /api/leaderboards/` - Leaderboard data
- `GET /api/user-progress/` - Current user's detailed progress
- `GET /api/stats/` - Platform-wide statistics

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False` in production
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving (WhiteNoise or CDN)
4. Configure email backend for notifications
5. Set up monitoring and logging
6. Enable HTTPS with SSL certificates
7. Configure backup strategies

### Scaling Considerations

- **Database Optimization**: Add indexes for frequently queried fields
- **Caching**: Implement Redis for session and query caching
- **Media Storage**: Use cloud storage for user uploads
- **Load Balancing**: Configure multiple server instances
- **CDN**: Serve static assets through a content delivery network

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review existing issues
- Contact the development team

## 🎉 Acknowledgments

- Bootstrap for the responsive UI framework
- Font Awesome for icons
- Django REST Framework for API functionality
- All contributors and beta testers

---

**Making environmental education engaging and action-driven! 🌱**
