<template>
  <div class="home-page">
    <div class="info-banner theme-dark">
      <div class="info-banner-contents">
        <div class="abstract">
          <h2 class="project-cta">
            Gain a <mark>Full</mark> Picture of the Adversary
          </h2>
          <p class="project-description">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
            cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
            non proident, sunt in culpa qui officia deserunt.
          </p>
          <a class="learn-more" href="/about">
            Learn More
          </a>
        </div>
        <div class="partners">
          <p>Research Conducted By:</p>
          <img class="ctid-logo" src="@/assets/images/ctid_logo_horizontal.png" />
        </div>
      </div>
    </div>
    <div class="tool-set theme-dark">
      <div class="tool-set-contents">
        <div class="tool-tabs">
          <template v-for="(tool, i) of tools" :key="tool.component">
            <h6 :class="['tool-tab', { 'theme-light': activeTool === i }]" @click="activeTool = i">
              {{ tool.name }}
            </h6>
          </template>
        </div>
      </div>
    </div>
    <div class="active-tool">
      <div class="active-tool-contents">
        <component class="active-tool-component" :is="tools[activeTool].component" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import PredictTechniquesTool from "@/components/Elements/PredictTechniquesTool.vue";

export default defineComponent({
  name: "App",
  data: () => ({
    tools: [
      {
        name: "Predict Techniques",
        component: "PredictTechniquesTool"
      },
      {
        name: "Relate Techniques",
        component: "PredictTechniquesTool"
      }
    ],
    activeTool: 0
  }),
  computed: {

  },
  methods: {

  },
  components: { PredictTechniquesTool }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.info-banner {
  display: flex;
  justify-content: center;
  width: 100%;
}

.info-banner-contents {
  display: flex;
  width: 100%;
  min-width: 0;
  max-width: scale.$max-width;
  padding: scale.size("xxl") scale.size("xxh") scale.size("xxh");
}

.partners {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: end;
  justify-content: end;
  margin-left: scale.size("xxh");
}

.partners p {
  margin-bottom: scale.size("s");
}

.project-cta {
  margin-bottom: scale.size("xs");
}

.project-description {
  margin-bottom: scale.size("xh");
}

.ctid-logo {
  max-width: 300px;
}

@media only screen and (max-width: scale.$tablet-width) {
  .partners {
    display: none;
  }
}

.tool-set,
.active-tool {
  display: flex;
  justify-content: center;
  width: 100%;
}

.tool-set-contents,
.active-tool-contents {
  display: flex;
  width: 100%;
  max-width: scale.$max-width;
}

.tool-set-contents {
  min-width: 0;
  padding: 0em scale.size("h");
}

.active-tool-contents {
  min-width: 0;
  padding: 0em scale.size("h");
}

.tool-tabs,
.active-tool-component {
  display: flex;
}

.active-tool-component {
  width: 100%;
  flex-direction: column;
}

.tool-tab {
  padding: scale.size("xs") scale.size("m");
  user-select: none;
  cursor: pointer;
}
</style>
