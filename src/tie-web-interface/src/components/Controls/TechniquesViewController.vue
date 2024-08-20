<template>
  <div :class="['technique-view-controller', { 'menu-active': active }]">
    <div class="view-controls">
      <ButtonMenu class="menu" @menu-open="active = true" @menu-close="active = false">
        <template #button>
          <OrganizeArrows class="icon" /><span>Organize</span>
        </template>
        <template #menuHeader>
          <mark>
            <OrganizeArrows class="header-icon" />
          </mark>
          <h4>Organize</h4>
        </template>
        <template #menuBody>
          <template v-for="v, k of view.organizations" :key="k">
            <DynamicViewControl class="control" :control="v" @execute="execute" />
          </template>
        </template>
      </ButtonMenu>
      <ButtonMenu class="menu" @menu-open="active = true" @menu-close="active = false">
        <template #button>
          <FilterStack class="icon" /><span>Filter</span>
        </template>
        <template #menuHeader>
          <mark>
            <FilterStack class="header-icon" />
          </mark>
          <h4>Filter</h4>
        </template>
        <template #menuBody>
          <template v-for="v, k of view.filters" :key="k">
            <DynamicViewControl class="control" :control="v" @execute="execute" />
          </template>
        </template>
      </ButtonMenu>
    </div>
    <ButtonList class="view-export">
      <template #button>
        <DownloadArrow class="icon" /><span>Save</span>
      </template>
      <template #buttonList>
        <button class="export" @click="downloadViewAsNavigatorLayer()">
          <DownloadArrow class="icon" /><span>Navigator Layer</span>
        </button>
        <button class="export" @click="downloadViewAsCsv()">
          <DownloadArrow class="icon" /><span>.CSV</span>
        </button>
      </template>
    </ButtonList>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent, type PropType } from "vue";
import type { PredictionsView } from "@/assets/scripts/PredictionsView";
import type { ControlCommand } from "@/assets/scripts/PredictionsView/Commands";
// Components
import ButtonList from "./ButtonList.vue";
import ButtonMenu from "./ButtonMenu.vue";
import FilterStack from "../Icons/FilterStack.vue";
import DownloadArrow from "../Icons/DownloadArrow.vue";
import OrganizeArrows from "../Icons/OrganizeArrows.vue";
import DynamicViewControl from "./ControlFields/DynamicViewControl.vue";

export default defineComponent({
  name: "TechniquesViewController",
  props: {
    view: {
      type: Object as PropType<PredictionsView>,
      required: true
    }
  },
  data: () => ({
    active: false,
  }),
  emits: ["execute", "download"],
  methods: {

    /**
     * Execute behavior.
     * @param cmd
     *  The command to execute.
     */
    execute(cmd: ControlCommand) {
      this.$emit("execute", cmd);
    },

    /**
     * Downloads the current view as a CSV file.
     */
    downloadViewAsCsv() {
      const contents = this.view.exportViewToCsv();
      this.$emit("download", "csv", contents);
    },

    /**
     * Downloads the current view as an Attack Navigator Layer.
     */
    downloadViewAsNavigatorLayer() {
      const contents = this.view.exportViewToNavigatorLayer(false);
      this.$emit("download", "navigator_layer", contents);
    }

  },
  components: {
    ButtonList, ButtonMenu, FilterStack, DownloadArrow,
    OrganizeArrows, DynamicViewControl
  }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.technique-view-controller {
  display: flex;
  justify-content: space-between;
}

/** === View Controls === */

.view-controls {
  display: flex;
}

.menu {
  margin-right: scale.size("m");
}

.menu:last-child {
  margin-right: 0em;
}

.menu :deep(button) {
  transition: opacity 0.1s ease-in-out;
}

.menu-active {
  .menu:not(.menu-open) :deep(button) {
    opacity: 0.5;
  }
}

mark {
  display: flex;
}

.header-icon {
  height: scale.size("m");
  margin-right: scale.size("s");
}

.control {
  margin-bottom: scale.size("xl");
}

.control:last-child {
  margin-bottom: 0em;
}
</style>
