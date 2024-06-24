<template>
  <div :class="['options-list-field', { flip }]">
    <div class="options-container">
      <div class="options-scrollbox" ref="scrollbox" :style="style">
        <ul class="options" v-if="hasOptions">
          <li ref="items" v-for="option in options" :key="option.value ?? 'null'" :list-id="option.value"
            :class="{ active: isActive(option) }" @click="$emit('select', option.value)" @mouseenter="setActive(option)"
            exit-focus-box>
            <span>{{ option.text }}</span>
          </li>
        </ul>
        <div class="no-options" v-else>
          No results found
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue";

export default defineComponent({
  name: "OptionsList",
  props: {
    options: {
      type: Array as PropType<{ value: string | null, text: string }[]>,
      required: true
    },
    select: {
      type: String as PropType<string | null>
    },
    maxHeight: {
      type: Number,
      default: 195
    }
  },
  data() {
    return {
      flip: false
    }
  },
  computed: {

    /**
     * Tests if there are any options available.
     * @returns
     *  True if there are options available, false otherwise.
     */
    hasOptions() {
      return 0 < this.options.length;
    },

    /**
     * Returns the option list's style.
     * @returns
     *  The option list's style.
     */
    style(): { maxHeight: string } {
      return { maxHeight: `${this.maxHeight}px` };
    }

  },
  emits: ["hover", "select"],
  methods: {

    /**
     * Tests if an option is active.
     * @returns
     *  True if the option is active, false otherwise.
     */
    isActive(option: Option) {
      return this.select === option.value;
    },

    /**
     * Sets the active option.
     * @param option
     *  The option.
     */
    setActive(option: Option) {
      this.$emit("hover", option.value);
    },

    /**
     * Brings an item into focus at the top of the list.
     * @param value
     *  The value to bring into focus.
     */
    focusItemTop(value: string | null) {
      let item = this.getItemElement(value);
      let scrollbox = this.$refs.scrollbox as HTMLElement;
      // Update scroll position
      if (item) {
        scrollbox.scrollTop = item.offsetTop;
      }
    },

    /**
     * Brings an item into focus.
     * @param value
     *  The value to bring into focus.
     */
    bringItemIntoFocus(value: string | null) {
      let item = this.getItemElement(value);
      let scrollbox = this.$refs.scrollbox as HTMLElement;
      // Update scroll position
      if (item) {
        let { top: itTop, bottom: itBottom } = item.getBoundingClientRect();
        let { top: elTop, bottom: elBottom } = scrollbox.getBoundingClientRect();
        if (itTop < elTop) {
          scrollbox.scrollTop = item.offsetTop;
        }
        else if (elBottom < itBottom) {
          let offsetHeight = (elBottom - elTop) - (itBottom - itTop);
          scrollbox.scrollTop = item.offsetTop - offsetHeight;
        }
      }
    },

    /**
     * Get an item's {@link HTMLElement} from the list.
     * @param value
     *  The value.
     * @returns
     *  The {@link HTMLElement}. `undefined` if the item doesn't exist.
     */
    getItemElement(value: string | null): HTMLElement | undefined {
      let item: HTMLElement | undefined = undefined;
      if (!this.$refs.items) {
        return item;
      }
      for (let el of this.$refs.items as HTMLElement[]) {
        if (value === el.getAttribute("list-id")) {
          item = el as HTMLElement;
          break;
        }
      }
      return item;
    }

  },
  mounted() {

    /**
     * Developer's Note:
     * If an <OptionsList> does not extend past the bottom of the document's body or its
     * parent <ScrollBox>, it's deemed visible. These checks do not account for any
     * other scroll constructs and do not account for nested <ScrollBox>'s.
     */

    // Resolve parent
    let sc = "scroll-content";
    let ele = this.$refs.scrollbox as HTMLElement;
    let par = this.$el.parentElement;
    let body = document.body;
    while (par !== body && !par.classList.contains(sc)) {
      par = par.parentElement;
    }
    // Resolve overlap
    let { bottom: b1 } = par.getBoundingClientRect();
    let { bottom: b2 } = ele.getBoundingClientRect();
    if (b1 < b2) {
      this.flip = true;
    } else {
      this.flip = false;
    }
    // Focus selection
    if (this.select !== undefined) {
      this.focusItemTop(this.select);
    }
  }
});

/**
 * Option type
 */
type Option = {
  value: string | null,
  text: string
}

</script>

<style scoped lang="scss">
@use "@/assets/styles/engenuity_color_system.scss" as color;
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

/** === Main Field === */

.options-container {
  @include color.shadow;
  position: absolute;
  width: 100%;
  border-width: 1px;
  box-sizing: border-box;
  background: inherit;
}

.options-list-field:not(.flip) .options-container {
  top: 0%;
  padding-top: scale.size("xh");
  border-style: none solid solid solid;
}

.options-list-field.flip .options-container {
  bottom: 0%;
  padding-bottom: scale.size("xh");
  border-style: solid solid none solid;
}

.options-scrollbox {
  overflow-y: scroll;
  overflow-x: hidden;
}

/** === Options List === */

.options {
  position: relative;
  padding: 0em;
}

.options li {
  @include color.dormant-list-item;
  display: flex;
  align-items: center;
  list-style: none;
  user-select: none;
  height: scale.size("xxl");
  padding: 0em 2 * scale.size("m");
}

.options span {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

/** === Options Hover === */

.options li.active,
.options li.active.null {
  @include color.active-list-item;
  padding-left: scale.size("m");
  border-left-style: solid;
  border-left-width: scale.size("m");
}

/** === No Options === */

.no-options {
  @include color.placeholder;
  display: flex;
  align-items: center;
  user-select: none;
  height: scale.size("xh");
  padding: 0em scale.size("m");
}
</style>
