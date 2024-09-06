<template>
  <NavigationHeader id="page-header" :pageLinks />
  <div id="page-contents">
    <div id="page-router">
      <RouterView />
    </div>
    <div id="page-footer">
      <NavigationFooter />
    </div>
  </div>
</template>

<script lang="ts">
// Test
// Dependencies
import { defineComponent, provide } from "vue";
import { useInferenceEngineStore } from "./stores/InferenceEngineStore";
// Components
import { RouterView } from 'vue-router'
import NavigationHeader from "./components/Controls/NavigationHeader.vue";
import NavigationFooter from "./components/Controls/NavigationFooter.vue";

export default defineComponent({
  name: "App",
  setup() {
    provide(
      "lockPageScroll",
      (lock: boolean) => {
        document.body.style.overflow = lock ? "hidden" : "";
      }
    )
  },
  data: () => ({
    engine: useInferenceEngineStore(),
    pageLinks: [
      {
        name: "Home",
        url: "/",
        sections: []
      },
      {
        name: "About",
        url: "/about",
        sections: [
          {
            name: "Learn More",
            description: "Learn about the project.",
            url: "/about"
          },
          {
            name: "Our Dataset",
            description: "Learn about our training data.",
            url: "/about#dataset"
          }
        ]
      },
      {
        name: "Resources",
        url: "/resources",
        sections: [
          {
            name: "Use the Python Notebook",
            description: "Run the Engine locally on your machine.",
            url: "/resources/"
          },
          {
            name: "Contribute",
            description: "Learn how to contribute.",
            url: "https://github.com/center-for-threat-informed-defense/technique-inference-engine?tab=readme-ov-file#getting-involved"
          }
        ]
      },
    ]
  }),
  computed: {

  },
  async mounted() {
    // Warmup Inference Engine
    await this.engine.warmup();
  },
  components: { RouterView, NavigationHeader, NavigationFooter }
});
</script>

<style lang="scss">
#app {
  display: flex;
  flex-direction: column;
}

#page-header {
  width: 100%;
  flex-shrink: 0;
}

#page-contents {
  flex: 1;
  display: flex;
  flex-direction: column;
}

#page-router {
  flex: 1;
}
</style>
