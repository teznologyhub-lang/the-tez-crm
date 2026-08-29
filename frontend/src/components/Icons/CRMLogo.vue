<template>
  <svg
    width="300"
    height="300"
    viewBox="0 0 300 300"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="tez-bg" x1="0" y1="0" x2="300" y2="300" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="#1a1a3e"/>
        <stop offset="100%" stop-color="#0f2057"/>
      </linearGradient>
      <linearGradient id="tez-glow" x1="150" y1="80" x2="150" y2="220" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="#6ee7ff"/>
        <stop offset="100%" stop-color="#ffffff"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <!-- Background rounded square -->
    <rect width="300" height="300" rx="64" ry="64" fill="url(#tez-bg)"/>
    <!-- T lettermark -->
    <g filter="url(#glow)">
      <!-- Horizontal bar of T -->
      <rect x="68" y="82" width="164" height="44" rx="12" fill="url(#tez-glow)"/>
      <!-- Vertical stem of T -->
      <rect x="121" y="82" width="58" height="136" rx="12" fill="url(#tez-glow)"/>
    </g>
  </svg>
</template>
