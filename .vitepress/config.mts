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
      { text: "Vehicles", link: "/vehicles/corolt-2b" },
      { text: "Missions", link: "/missions/csa-04" },
      { text: "Comunicats", link: "/social_media/csa-04_post" },
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
          { text: "Corolt-Ib (Coet Sonda Millorat)", link: "/vehicles/corolt-1b" },
          { text: "Corolt-II (Multietapa Espacial)", link: "/vehicles/corolt-2" },
          { text: "Corolt-IIb (Variant Radial)", link: "/vehicles/corolt-2b" },
        ]
      },
      {
        text: "Diari de Vol",
        items: [
          { text: "CSA-01: Vol Inaugural", link: "/missions/csa-01" },
          { text: "CSA-02: Vol Operatiu Corolt-Ib", link: "/missions/csa-02" },
          { text: "CSA-03: Assalt Estratosfèric", link: "/missions/csa-03" },
          { text: "CSA-04: El Desafiament Corolt-IIb", link: "/missions/csa-04" },
          { text: "Plantilla de Missió", link: "/missions/template_mission" },
        ]
      },
      {
        text: "Prensa i Xarxes",
        items: [
          { text: "Comunicat CSA-01", link: "/social_media/csa-01_post" },
          { text: "Comunicat CSA-02", link: "/social_media/csa-02_post" },
          { text: "Comunicat CSA-03", link: "/social_media/csa-03_post" },
          { text: "Comunicat CSA-04", link: "/social_media/csa-04_post" },
          { text: "Plantilla de Comunicat", link: "/social_media/template_post" },
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
