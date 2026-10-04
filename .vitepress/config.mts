import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Corolt Space Agency",
  description: "Official flight log, telemetry analysis, and aerospace engineering portal.",
  base: "/csa/",
  themeConfig: {
    logo: "/assets/flag.png",
    siteTitle: "CSA Operations",
    nav: [
      { text: "Home", link: "/" },
      { text: "Science", link: "/science/" },
      { text: "Vehicles", link: "/vehicles/corolt-3" },
      { text: "Missions", link: "/missions/csa-07" },
      { text: "Press", link: "/social_media/csa-07_post" },
      { text: "GitHub", link: "https://github.com/Elebrimir/csa" }
    ],
    sidebar: [
      {
        text: "Space Agency",
        items: [
          { text: "Manifesto & Goals", link: "/" },
          { text: "Kerbin Science Matrix", link: "/science/" },
        ]
      },
      {
        text: "Vehicle Fleet",
        items: [
          { text: "Corolt-I (Sounding Rocket)", link: "/vehicles/corolt-1" },
          { text: "Corolt-Ib (Upgraded Sounding Rocket)", link: "/vehicles/corolt-1b" },
          { text: "Corolt-II (Multi-Stage Launcher)", link: "/vehicles/corolt-2" },
          { text: "Corolt-IIb (Radial Booster Variant)", link: "/vehicles/corolt-2b" },
          { text: "Corolt-III (Tandem Orbital Launcher)", link: "/vehicles/corolt-3" },
          { text: "Corolt-IIIb (Active Guidance Variant)", link: "/vehicles/corolt-3b" },
        ]
      },
      {
        text: "Flight Log",
        items: [
          { text: "CSA-01: Maiden Flight", link: "/missions/csa-01" },
          { text: "CSA-02: Corolt-Ib Operational Flight", link: "/missions/csa-02" },
          { text: "CSA-03: Stratospheric Assault", link: "/missions/csa-03" },
          { text: "CSA-04: The Corolt-IIb Challenge", link: "/missions/csa-04" },
          { text: "CSA-05: Corolt-III Debut", link: "/missions/csa-05" },
          { text: "CSA-05b: Space Leap (240 km)", link: "/missions/csa-05b" },
          { text: "CSA-06: kOS Guidance & Recovery", link: "/missions/csa-06" },
          { text: "CSA-07: Mobile Control & Splashdown", link: "/missions/csa-07" },
          { text: "Mission Template", link: "/missions/template_mission" },
        ]
      },
      {
        text: "Press & Social Media",
        items: [
          { text: "CSA-01 Release", link: "/social_media/csa-01_post" },
          { text: "CSA-02 Release", link: "/social_media/csa-02_post" },
          { text: "CSA-03 Release", link: "/social_media/csa-03_post" },
          { text: "CSA-04 Release", link: "/social_media/csa-04_post" },
          { text: "CSA-05 Release", link: "/social_media/csa-05_post" },
          { text: "CSA-05b Release", link: "/social_media/csa-05b_post" },
          { text: "CSA-06 Release", link: "/social_media/csa-06_post" },
          { text: "CSA-07 Release", link: "/social_media/csa-07_post" },
          { text: "Release Template", link: "/social_media/template_post" },
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Elebrimir/csa' }
    ],
    footer: {
      message: 'Ad Astra Per Scientiam',
      copyright: 'Copyright © 2026 Corolt Space Agency (CSA)'
    }
  }
})
