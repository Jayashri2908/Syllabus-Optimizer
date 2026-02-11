
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check local storage for existing session
        const storedUser = localStorage.getItem('syllabus_opt_user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error("Failed to parse user data", e);
                localStorage.removeItem('syllabus_opt_user');
            }
        }
        setLoading(false);
    }, []);

    const login = (credentials) => {
        // Mock login - checks against a "database" in local storage or just succeeds for now if strictly local
        // For this requirement ("simplest possible way... all local"), we'll simulating matching against registered users
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const users = JSON.parse(localStorage.getItem('syllabus_opt_users_db') || '[]');
                const foundUser = users.find(u => (u.username === credentials.identifier || u.email === credentials.identifier) && u.password === credentials.password);

                if (foundUser) {
                    const { password, ...safeUser } = foundUser; // exclude password from session
                    setUser(safeUser);
                    localStorage.setItem('syllabus_opt_user', JSON.stringify(safeUser));
                    resolve(safeUser);
                } else {
                    reject(new Error("Invalid credentials"));
                }
            }, 500); // Fake delay
        });
    };

    const signup = (userData) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const users = JSON.parse(localStorage.getItem('syllabus_opt_users_db') || '[]');

                if (users.find(u => u.username === userData.username)) {
                    reject(new Error("Username already taken"));
                    return;
                }
                if (users.find(u => u.email === userData.email)) {
                    reject(new Error("Email already registered"));
                    return;
                }

                const newUser = { ...userData, id: Date.now().toString() };
                users.push(newUser);
                localStorage.setItem('syllabus_opt_users_db', JSON.stringify(users));

                // Auto login after signup
                const { password, ...safeUser } = newUser;
                setUser(safeUser);
                localStorage.setItem('syllabus_opt_user', JSON.stringify(safeUser));

                resolve(safeUser);
            }, 800);
        });
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('syllabus_opt_user');
    };

    return (
        <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
