import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Lock } from 'lucide-react';

export default function Login() {
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    // Get the path the user was trying to access
    const from = location.state?.from?.pathname || '/';

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!pin.trim()) {
            setError('Please enter a PIN');
            return;
        }

        // Store the PIN in localStorage
        localStorage.setItem('job_tracker_pin', pin);

        // Redirect to the originally requested page, or dashboard
        navigate(from, { replace: true });
    };

    return (
        <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <div className="flex justify-center">
                    <div className="bg-blue-500/10 p-4 rounded-2xl ring-1 ring-blue-500/20">
                        <Lock className="h-12 w-12 text-blue-400" />
                    </div>
                </div>
                <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                    Job Tracker Pro
                </h2>
                <p className="mt-2 text-center text-sm text-slate-400">
                    Restricted Access — Please enter your PIN
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-slate-800/50 backdrop-blur border border-slate-700 py-8 px-4 shadow sm:rounded-xl sm:px-10">
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div>
                            <label htmlFor="pin" className="block text-sm font-medium text-slate-300">
                                Secret PIN
                            </label>
                            <div className="mt-1">
                                <input
                                    id="pin"
                                    name="pin"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    value={pin}
                                    onChange={(e) => {
                                        setPin(e.target.value);
                                        setError('');
                                    }}
                                    className="appearance-none block w-full px-3 py-2 border border-slate-600 rounded-lg shadow-sm placeholder-slate-500 bg-slate-900/50 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                    placeholder="Enter your access PIN"
                                />
                            </div>
                            {error && (
                                <p className="mt-2 text-sm text-red-500 font-medium">
                                    {error}
                                </p>
                            )}
                        </div>

                        <div>
                            <button
                                type="submit"
                                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-blue-500 transition-colors"
                            >
                                Unlock App
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
