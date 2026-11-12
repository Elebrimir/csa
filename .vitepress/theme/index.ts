import DefaultTheme from 'vitepress/theme'
import './custom.css'
import ConstellationVisualizer from './components/ConstellationVisualizer.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ConstellationVisualizer', ConstellationVisualizer)
  }
}
