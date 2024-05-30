<template>
  <NavigationHeader id="page-header" />
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
import { defineComponent } from "vue";
// Components
import { RouterView } from 'vue-router'
import NavigationHeader from "./components/Controls/NavigationHeader.vue";
import NavigationFooter from "./components/Controls/NavigationFooter.vue";

export default defineComponent({
  name: "App",
  data: () => ({
  }),
  computed: {

  },
  methods: {

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
