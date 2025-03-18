<template>
  <div :class="['navigation-control', { 'mobile-menu-open': mobile }]">
    <div class="navigation-sticky theme-dark">
      <div class="navigation-contents">
        <div class="page-logo-container">
          <HamburgerMenu :close="mobile" @click="openMobileMenu(!mobile)" />
          <RouterLink class="logo-text" to="/">
            Technique Inference Engine
          </RouterLink>
        </div>
        <div class="page-links-container">
          <ul class="page-links">
            <template v-for="l of pageLinks" :key="l.name">
              <li class="page-link link-hover-trigger">
                <component class="primary-link" :is="getLinkComp(l.url)" v-bind="getLinkProp(l.url)">
                  {{ l.name }}<span class="dropdown" v-if="l.sections?.length"></span>
                </component>
                <div class="section-links-container" v-if="l.sections?.length">
                  <ul class="section-links theme-light">
                    <template v-for="s of l.sections" :key="s.name">
                      <li class="section-link section-name-hover-trigger">
                        <component :is="getLinkComp(s.url)" v-bind="getLinkProp(s.url)">
                          <p class="section-name">{{ s.name }}</p>
                          <p class="section-description">{{ s.description }}</p>
                        </component>
                      </li>
                    </template>
                  </ul>
                </div>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </div>
    <div class="navigation-buffer theme-dark"></div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent, inject, type PropType } from "vue";
// Components
import { RouterLink } from 'vue-router'
import HamburgerMenu from "@/components/Icons/HamburgerMenu.vue";
import type { MainLink } from "./NavigationHeaderTypes";

export default defineComponent({
  name: "NavigationHeader",
  setup() {
    const lockPageScroll = inject<(l: boolean) => void>("lockPageScroll");
    return {
      lockPageScroll: lockPageScroll ?? (() => { })
    }
  },
  props: {
    pageLinks: {
      type: Array as PropType<MainLink[]>,
      required: true
    }
  },
  data: () => ({
    mobile: false
  }),
  methods: {

    /**
     * Open / Closes the mobile menu.
     * @param open
     *  True to open menu, false to close it.
     */
    openMobileMenu(open: boolean) {
      this.mobile = open;
      this.lockPageScroll(open);
    },

    /**
     * Given a link, returns the appropriate component.
     * @param link
     *  The link.
     */
    getLinkComp(link: string) {
      return link.startsWith("http") ? "a" : "RouterLink";
    },

    /**
     * Given a link, returns the appropriate component properties.
     * @param link
     *  The link.
     */
    getLinkProp(link: string) {
      return { [link.startsWith("http") ? 'href' : 'to']: link };
    }

  },
  watch: {
    '$route'() {
      this.openMobileMenu(false);
    }
  },
  components: { RouterLink, HamburgerMenu }
});
</script>

<style lang="scss" scoped>
@use 'sass:math';
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

$_fs : scale.font-size("h6");
$_lh : scale.line-height("h6");

/**
 * The header's padding.
 */
$header-padding: scale.size("h");

/*
 * The header's calculated height.
 */
$header-height: calc(($header-padding * 1.5) + ($_fs * $_lh / scale.$units));

/** === Main Control === */

.navigation-sticky {
  position: fixed;
  display: flex;
  justify-content: center;
  width: 100%;
  z-index: 2;
}

.navigation-contents {
  flex: 1;
  display: flex;
  justify-content: space-between;
  text-wrap: nowrap;
  max-width: scale.$max-width;
  padding: scale.size("xl") scale.size("xxl");
}

.navigation-buffer {
  height: $header-height;
}

/** === Navigation Logo === */

.page-logo-container {
  display: flex;
  align-items: center;
}

.hamburger-menu-icon {
  margin-right: scale.size("xxl");
}

.logo-icon {
  @include scale.box("l");
  border: solid 1px;
  margin-right: scale.size("s");
}

.logo-text {
  @include scale.h3;
  text-decoration: none;
}

/** === Navigation Links === */

.page-links,
.section-links {
  padding: 0em;
  list-style: none;
}

.page-links {
  @include color.dynamic-theme(("inherit", false),
    (scale.$mobile-width, "light"));
}

.invert .page-links {
  @include color.dynamic-theme(("inherit", false),
    (scale.$mobile-width, "dark"));
}

.primary-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.dropdown {
  margin-left: scale.size("xs");
  margin-bottom: scale.size("xxt");
}

.dropdown::after {
  content: "";
  display: block;
  width: scale.size("xxt");
  height: scale.size("xxt");
  border-style: none none solid solid;
  border-width: 1.5px;
  transform: rotate(-45deg);
}

/** === Navigation Links (Desktop) === */

@include scale.above-mobile-width() {

  .hamburger-menu-icon {
    display: none;
  }

  .page-links {
    display: flex;
    align-items: center;
  }

  .page-link {
    position: relative;
    margin-left: scale.size("xxl");
  }

  .page-link:first-child {
    margin-left: 0;
  }

  .primary-link {
    @include scale.h6;
  }

  .section-links-container {
    position: absolute;
    top: 100%;
    right: 0em;
    width: fit-content;
    padding-top: scale.size("m");
    opacity: 0;
    visibility: hidden;
    transform: translateY(- scale.size("s"));
    transition:
      opacity 0.2s ease-in-out 0.05s,
      visibility 0.2s ease-in-out 0.05s,
      transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) 0.45s;
    cursor: pointer;
  }

  .page-links-container {
    margin: auto 0;
  }

  .page-link:hover .section-links-container {
    opacity: 1;
    visibility: visible;
    transform: translateY(0em);
    transition:
      opacity 0.2s ease-in-out 0.05s,
      visibility 0.2s ease-in-out 0.05s,
      transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) 0.05s;
  }

  .section-links {
    @include color.shadow;
  }

  .section-link:nth-child(even) {
    background: #f0f1f2;
  }

  .section-link a {
    display: block;
    text-decoration: none;
    padding: scale.size("xxl");
  }

  .section-name {
    @include scale.learn-more;
    margin-bottom: scale.size("s");
  }

}

/** === Navigation Links (Mobile) === */

@include scale.at-and-below-mobile-width() {

  .page-links-container {
    position: fixed;
    top: $header-height;
    left: 0em;
    right: 0em;
    bottom: 0em;
    background: rgb(0 0 0 / 50%);
    opacity: 0;
    visibility: hidden;
    transition:
      opacity 0.25s ease-in-out 0s,
      visibility 0.25s ease-in-out 0s;
  }

  .page-links {
    max-height: calc(100vh - $header-height);
    padding: scale.size("h");
    box-sizing: border-box;
    overflow-y: scroll;
  }

  .page-link {
    margin-bottom: scale.size("xl");
    transform: translateX(- scale.size("h"));
    transition:
      transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .page-link:last-child {
    margin-bottom: 0em;
  }

  @for $index from 1 through 9 {
    .page-link:nth-child(#{ $index }) {
      transition-delay: $index * 0.025s;
    }
  }

  .primary-link {
    @include scale.h5;
  }

  .dropdown {
    display: none;
  }

  .section-links-container {
    @include color.accent-border;
    padding: 0em scale.size("xl");
    border-left-style: solid;
    border-left-width: 2px;
    margin-top: scale.size("xl");
  }

  .section-link a {
    display: block;
    text-decoration: none;
  }

  .section-link {
    margin-bottom: scale.size("l");
  }

  .section-link:last-child {
    margin-bottom: 0em;
  }

  .section-name {
    @include scale.h6;
    margin-bottom: scale.size("xxt");
  }

  .mobile-menu-open {

    .page-links-container {
      opacity: 1;
      visibility: visible;
    }

    .page-link {
      transform: translateX(0px);
    }

  }

}
</style>
