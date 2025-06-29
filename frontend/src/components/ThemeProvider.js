"use client";

import React from 'react';
import { ConfigProvider, theme } from 'antd';

export default function ThemeProvider({ children }) {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#d8fa70',
          colorBgBase: '#0a0a0a',
          colorTextBase: '#ffffff',
        },
      }}
    >
      {children}
    </ConfigProvider>
  );
}