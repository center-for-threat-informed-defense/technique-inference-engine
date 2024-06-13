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
            name: "Methodology",
            description: "Learn how we trained the model.",
            url: "/about"
          }
        ]
      },
      {
        name: "Methodology",
        url: "/about"
      },
      {
        name: "Help",
        url: "/about",
        sections: [
          {
            name: "Predicting Techniques",
            description: "Learn how to predict Techniques.",
            url: "/about"
          },
          {
            name: "Tuning the Model",
            description: "Learn how to tune the model.",
            url: "/about"
          },
          {
            name: "Contribute",
            description: "Learn how to contribute.",
            url: "/about"
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

<style>
#app {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
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
