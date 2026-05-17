import React from "react";
import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="top-nav">
      <div className="top-nav__brand">Blackjack CV</div>
      <nav className="top-nav__links">
        <NavLink
          to="/"
          className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
        >
          Home
        </NavLink>
        <NavLink
          to="/game"
          className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
        >
          Game
        </NavLink>
        <NavLink
          to="/history"
          className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
        >
          History
        </NavLink>
      </nav>
    </header>
  );
}