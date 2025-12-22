-- USERS table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    age INTEGER,
    club_team TEXT,
    hometown TEXT
);

-- SWIMS table
CREATE TABLE swims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    distance INTEGER NOT NULL,
    pool TEXT NOT NULL,
    stroke TEXT NOT NULL,
    duration REAL,
    difficulty INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- LIFTS table
CREATE TABLE lifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    exercise TEXT NOT NULL,
    sets INTEGER,
    reps INTEGER,
    weight INTEGER,
    muscle_group TEXT,
    rpe INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- RACES table
CREATE TABLE races (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    event TEXT NOT NULL,
    time TEXT,
    meet TEXT,
    round TEXT,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- RECOVERY table
CREATE TABLE recovery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sleep_hours REAL,
    fatigue INTEGER,
    soreness INTEGER,
    stress INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
