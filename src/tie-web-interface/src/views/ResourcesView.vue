<template>
  <div class="resources">
    <div class="resources-contents">
      <h1 id="notebook">Using the Python Notebook</h1>
      <p>
        If you're a machine learning engineer looking to experiment with your own instance of the Technique Inference
        Engine, we
        offer a Python Notebook containing all the necessary code to get started. The following sections will guide you
        through the process of setting up the Python Notebook and training your own TIE model.
      </p>
      <h2>Setting up the Project</h2>
      <h3>1. Clone the Repository</h3>
      <p>Begin by cloning the project's repository to your local machine:</p>
      <div class="codeblock">
        git clone https://github.com/center-for-threat-informed-defense/technique-inference-engine.git
      </div>
      <p>and <code>cd</code> into the cloned directory:</p>
      <div class="codeblock">
        cd technique-inference-engine
      </div>
      <h3>2. Install the Project's Dependencies</h3>
      <p>We highly recommend using <a href="https://python-poetry.org/">Poetry</a> to setup the project's
        virtual environment and dependencies.</p>
      <code>poetry install</code>
      <h3>3. Start Experimenting</h3>
      Open the Python Notebook located in <code>./notebooks/main.ipynb</code> in your editor of choice and get going!
      <img src="/images/python_notebook_standard.png" srcset="/images/python_notebook_retina.png 2x"
        style="max-width:850px;">
      <p>
        <i>For additional information, refer to the Technique Inference
          Engine's <a
            href="https://github.com/center-for-threat-informed-defense/technique-inference-engine">GitHub</a>.</i>
      </p>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Declarations
declare const MathJax: { typeset: () => void }

export default defineComponent({
  name: "AboutView",
  mounted() {
    MathJax.typeset();
  },
  updated() {
    MathJax.typeset();
  }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

.resources {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: scale.size("xxh") 0em;
}

.resources-contents {
  width: 100%;
  max-width: scale.$max-width;
  padding: 0em scale.size("xxh");
}

.resources-contents :first-child {
  margin-top: 0em;
}

.resources-contents :last-child {
  margin-bottom: 0em;
}

h1,
h2,
h3,
h4,
h5,
h6,
li,
ol,
p {
  margin: scale.size("s") 0em;
}

img {
  display: block;
  width: 100%;
  margin: scale.size("xxl") auto;
}

pre {
  word-break: break-all;
}
</style>
