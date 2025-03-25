'use client';

import React from 'react';
import Link from 'next/link';

export const Navbar = () => {
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left side - Logo and title */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-800 hover:text-gray-600">
                Platform Support IPE
              </Link>
            </div>
          </div>

          {/* Center - Quick Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/incidents/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              New Incident
            </Link>
            <Link
              href="/health"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Health Check
            </Link>
            <Link
              href="/metrics"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              View Metrics
            </Link>
          </div>

          {/* Right side - User menu */}
          <div className="flex items-center">
            <div className="ml-3 relative">
              <div className="flex items-center space-x-4">
                <button className="bg-gray-800 flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                  <span className="sr-only">Open user menu</span>
                  <div className="h-8 w-8 rounded-full bg-gray-500"></div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}; 