import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Corolt Space Agency",
  description: "Diari oficial de missions, telemetria i desenvolupament aeroespacial.",
  base: "/csa/",
  themeConfig: {
    logo: "/assets/flag.png",
    siteTitle: "CSA Operations",
    nav: [
      { text: "Inici", link: "/" },
      { text: "Vehicles", link: "/vehicles/corolt-1" },
      { text: "Missions", link: "/missions/template_mission" },
      { text: "Comunicats", link: "/social_media/template_post" },
      { text: "GitHub", link: "https://github.com/Elebrimir/csa" }
    ],
    sidebar: [
      {
        text: "Agència Espacial",
        items: [
          { text: "Manifest i Objectius", link: "/" },
        ]
      },
      {
        text: "Flota de Vehicles",
        items: [
          { text: "Corolt-I (Coet Sonda)", link: "/vehicles/corolt-1" },
        ]
      },
      {
        text: "Diari de Vol",
        items: [
          { text: "Plantilla de Missió", link: "/missions/template_mission" },
        ]
      },
      {
        text: "Prensa i Xarxes",
        items: [
          { text: "Comunicats de Premsa", link: "/social_media/template_post" },
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
