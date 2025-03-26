import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { IncidentProvider } from '../lib/contexts/IncidentContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Incident Resolution Platform',
  description: 'AI-powered incident management and resolution',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-gray-100">
      <body className={`${inter.className} h-full`}>
        <IncidentProvider>
          {children}
        </IncidentProvider>
      </body>
    </html>
  );
} 