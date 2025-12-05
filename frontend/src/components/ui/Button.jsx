import React from 'react';

const Button = ({ children, variant = 'primary', className = '', ...props }) => {
    const baseStyles = "px-4 py-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background";

    const variants = {
        primary: "bg-white text-black hover:bg-gray-200 focus:ring-white",
        secondary: "bg-surface-hover text-white border border-border hover:bg-border focus:ring-gray-500",
        accent: "bg-accent text-black hover:bg-opacity-90 shadow-[0_0_15px_rgba(0,255,157,0.3)] hover:shadow-[0_0_25px_rgba(0,255,157,0.5)] focus:ring-accent",
        danger: "bg-danger/10 text-danger border border-danger/20 hover:bg-danger/20 focus:ring-danger",
        ghost: "text-secondary hover:text-white hover:bg-white/5"
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;
