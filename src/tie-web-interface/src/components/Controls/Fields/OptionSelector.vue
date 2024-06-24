<template>
  <div class="option-selector-field light-theme">
    <OptionsList ref="optionsList" class="options-list theme-light" :select="select" :options="filteredOptions"
      :maxHeight="maxHeight" @hover="value => select = value" @select="selectOption" v-if="showMenu" />
    <div :class="['value-container', { 'menu-open': showMenu }]">
      <input type="text" ref="search" name="search" class="value-search"
        :placeholder="showMenu ? 'Search' : 'Add Technique'" @input="onSearchInput" @keydown="onSearchKeyDown"
        v-model="searchTerm" autocomplete="off" />
      <AddIcon class="add-icon" />
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { RawFocusBox, unsignedMod } from "@/assets/scripts/Utilities";
import { defineComponent, markRaw, type PropType } from "vue";
// Components
import AddIcon from "@/components/Icons/AddIcon.vue";
import OptionsList from "./OptionsList.vue";

export default defineComponent({
  name: "OptionsSelector",
  props: {
    options: {
      type: Object as PropType<Map<string, string>>,
      required: true
    },
    placeholder: {
      type: String,
      default: "-"
    },
    maxHeight: {
      type: Number,
      default: 195
    }
  },
  data() {
    return {
      select: null as string | null,
      showMenu: false,
      searchTerm: "",
      focusBox: markRaw(new RawFocusBox("click"))
    }
  },
  computed: {

    /**
     * Returns the filtered set of options.
     * @returns
     *  The filtered set of options.
     */
    filteredOptions(): { value: string | null, text: string }[] {
      let options: { value: string | null, text: string }[] = [];
      let st = this.searchTerm.toLocaleLowerCase();
      for (let [value, text] of this.options) {
        if (st === "" || text.toLocaleLowerCase().includes(st)) {
          options.push({ value, text });
        }
      }
      return options;
    },

    /**
     * Returns the scrollbox's style.
     * @returns
     *  The scrollbox's style.
     */
    style(): { maxHeight: string } {
      return { maxHeight: `${this.maxHeight}px` };
    }

  },
  emits: ["select"],
  methods: {

    /**
     * Field focus in behavior.
     */
    onFocusIn() {
      if (this.showMenu) {
        return;
      }
      // Open menu
      this.showMenu = true;
      // Reset select
      this.select = this.filteredOptions[0]?.value;
    },

    /**
     * Field focus out behavior.
     */
    onFocusOut() {
      if (!this.showMenu) {
        return;
      }
      // Close menu
      this.showMenu = false;
      // Clear search
      this.searchTerm = "";
      // Reset select
      this.select = null;
    },

    /**
     * Search field input behavior.
     */
    onSearchInput() {
      // Update select
      this.select = this.filteredOptions[0]?.value;
      // Focus selection
      let optionsList = this.$refs.optionsList as any;
      optionsList?.focusItemTop(this.select);
    },

    /**
     * Search field keydown behavior.
     * @param event
     *  The keydown event.
     */
    onSearchKeyDown(event: KeyboardEvent) {
      let idx;
      let options = this.filteredOptions;
      let optionsList = this.$refs.optionsList as any;
      switch (event.key) {
        case "ArrowUp":
          if (!options.length) {
            return;
          }
          event.preventDefault();
          // Resolve index
          idx = options.findIndex(o => o.value === this.select);
          idx = unsignedMod(idx - 1, options.length);
          // Update selection
          this.select = options[idx].value;
          optionsList?.bringItemIntoFocus(this.select);
          break;
        case "ArrowDown":
          if (!options.length) {
            return;
          }
          event.preventDefault();
          // Resolve index
          idx = options.findIndex(o => o.value === this.select);
          idx = unsignedMod(idx + 1, options.length);
          // Update selection
          this.select = options[idx].value;
          optionsList?.bringItemIntoFocus(this.select);
          break;
        case "Tab":
        case "Enter":
          event.preventDefault();
          // Update value
          this.selectOption(this.select);
          // Force search field out of focus
          (this.$refs.search as any)!.blur();
          break;
      }
    },

    /**
     * Emits the selected option.
     * @param value
     *  The selected option.
     */
    selectOption(value: string | null) {
      if (value) {
        this.$emit("select", value);
      }
    }

  },
  mounted() {
    this.focusBox.mount(
      this.$el,
      this.onFocusIn,
      this.onFocusOut
    );
  },
  unmounted() {
    this.focusBox.destroy()
  },
  components: { AddIcon, OptionsList }
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/engenuity_color_system.scss" as color;
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

/** === Main Field === */

.option-selector-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr);
  user-select: none;
  height: scale.size("xh");
  cursor: pointer;
}

/** === Value Container === */

.value-container {
  grid-area: 1 / 1;
  display: flex;
  align-items: center;
  position: relative;
  border: solid 1px;
  box-sizing: border-box;
  z-index: 1;
}

.value-container:not(.menu-open) {
  @include color.field-border;
}

.options-list {
  z-index: 1;
}

.options-list:not(.flip)+.value-container.menu-open {
  border-style: solid;
  border-bottom: none;
}

.options-list.flip+.value-container.menu-open {
  border-style: solid;
  border-top: none;
}

/** === Value Search === */

.value-search {
  flex: 1;
  color: inherit;
  font-size: inherit;
  font-weight: inherit;
  font-family: inherit;
  height: 100%;
  min-width: 0em;
  padding: 0em scale.size("l");
  border: none;
  background: none;
}

.value-search:focus {
  outline: none;
}

.value-search::placeholder {
  @include color.placeholder;
  opacity: 1;
}

.value-container:not(.menu-open) .value-search::placeholder {
  @include scale.placeholder;
}

.add-icon {
  @include color.icon;
  padding-right: scale.size("l");
}

/** === Dropdown Options === */

.options-list {
  grid-area: 1 / 1;
  position: relative;
}
</style>
