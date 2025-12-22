# SwimJournal

#### Video Demo:
https://www.youtube.com/watch?v=39S1PSs4N6o

#### Description:
SwimJournal is a full-stack web application designed to help swimmers systematically track, analyze, and reflect on their training across multiple dimensions. The application serves as a centralized digital training log where athletes can record swim workouts, strength training sessions, race performances, and recovery metrics, all within a single, cohesive platform. The purpose of SwimJournal is to transform raw training data into meaningful insights that promote consistency, self-awareness, and long-term athletic development.

Many swimmers rely on fragmented tools such as handwritten notebooks, phone notes, or spreadsheets to record training, which makes it difficult to identify trends, measure progress, or maintain consistency over time. SwimJournal addresses this problem by consolidating all training-related information into a structured database that is accessible from anywhere. By organizing training data chronologically and presenting summaries visually, the app allows users to better understand how their habits impact performance.

Users begin by creating a personal account and logging in securely. Authentication is implemented using hashed passwords and Flask session management to ensure user data remains private and protected. Each user only has access to their own entries, and all database queries are filtered by user ID to enforce data isolation. Once logged in, users are taken to a personalized dashboard that acts as the central hub of the application.

The dashboard provides a high-level overview of the user’s recent training activity. It displays weekly training summaries such as total swim yardage completed, the number of lift sessions performed, and the average soreness level recorded during recovery. In addition, the dashboard calculates and displays two different streak metrics: a training streak and an activity streak. These streaks are automatically computed based on consecutive days of logged activity and are intended to motivate users to maintain consistent training habits.

SwimJournal includes dedicated pages for each major component of training. The swim logging feature allows users to record details such as date, distance, stroke type, pool type, duration, difficulty level, and optional notes. Strength training sessions can be logged with exercises, sets, repetitions, weight, muscle group, perceived exertion, and personal notes. Race results can be recorded with event name, race time, meet name, round, and reflections, allowing swimmers to contextualize their performances beyond just times.

Recovery tracking is another core feature of the application. Users can log sleep duration, fatigue level, soreness, stress, and recovery notes. This emphasizes the importance of rest and recovery alongside physical training and encourages athletes to recognize how recovery metrics influence performance outcomes.

The progression page provides a visual representation of race performance over time using Chart.js. Race times are converted into seconds and plotted on a line chart where faster times appear higher on the graph, making improvement intuitive to interpret. Users can select specific events from a dropdown menu to view event-based progression, helping them identify trends and evaluate performance changes over multiple competitions.

From a technical standpoint, the backend of SwimJournal is built using Flask and SQLite. Flask handles routing, form processing, session management, and application logic, while SQLite provides a lightweight relational database suitable for this type of application. SQL queries are used to insert, update, delete, and retrieve training data, as well as to compute weekly summaries and streak calculations.

The frontend is implemented using HTML, CSS, Bootstrap, and JavaScript. Bootstrap provides a responsive layout and consistent UI components, while custom CSS is used to create a cohesive blue-themed design with optional dark and light modes. The application layout features a persistent sidebar for navigation, ensuring ease of use and clear information hierarchy across all pages.

SwimJournal was developed as my final project for CS50x and represents the integration of concepts learned throughout the course, including programming fundamentals, database design, web development, and software architecture. The project reflects both my technical growth and my personal experience as a competitive swimmer, combining computer science with a real-world use case in a meaningful and practical way.
