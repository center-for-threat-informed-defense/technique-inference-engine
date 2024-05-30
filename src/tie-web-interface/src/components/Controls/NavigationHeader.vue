<template>
  <div class="navigation-control">
    <div class="navigation-sticky theme-dark">
      <div class="navigation-contents">
        <div class="page-logo-container">
          <div class="navigation-burger" @click="mobileNav = !mobileNav">
            =
          </div>
          <div class="logo-icon"></div>
          <RouterLink class="logo-text" to="/">
            Technique Inference Engine
          </RouterLink>
        </div>
        <div class="page-links-container">
          <ul class="page-links">
            <li class="page-link link-hover-trigger" v-for="link of links" :key="link.name">
              <RouterLink class="primary-link" :to="link.url">
                {{ link.name }}<span class="dropdown" v-if="link.sections?.length"></span>
              </RouterLink>
              <div class="section-links-container">
                <ul class="section-links theme-light" v-if="link.sections?.length">
                  <template v-for="section of link.sections" :key="section.name">
                    <li class="section-link section-name-hover-trigger">
                      <RouterLink :to="section.url">
                        <p class="section-name">{{ section.name }}</p>
                        <p class="section-description">{{ section.description }}</p>
                      </RouterLink>
                    </li>
                  </template>
                </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="navigation-buffer theme-dark"></div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import { RouterLink } from 'vue-router'

export default defineComponent({
  name: "NavigationHeader",
  data: () => ({
    mobileNav: false,
    links: [
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
  components: { RouterLink }
});
</script>

<style lang="scss" scoped>
@use 'sass:math';
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

$_fs : scale.font-size("h5");
$_lh : scale.line-height("h5");
$_pad : scale.size("h");

/*
 * The header's calculated height.
 */
$header-height: calc(($_pad * 2) + ($_fs * $_lh / scale.$units));

/** === Main Control === */

.navigation-sticky {
  position: fixed;
  display: flex;
  justify-content: center;
  width: 100%;
}

.navigation-contents {
  flex: 1;
  display: flex;
  justify-content: space-between;
  text-wrap: nowrap;
  max-width: scale.$max-width;
  padding: scale.size("h") scale.size("xxl");
}

.navigation-buffer {
  $fs: scale.font-size("h5");
  $lh: scale.line-height("h5");
  height: $header-height;
}

/** === Navigation Logo === */

.page-logo-container {
  display: flex;
  align-items: center;
}

.navigation-burger {
  margin-right: scale.size("s");
}

.logo-icon {
  @include scale.box("l");
  margin-right: scale.size("s");
  border: solid 1px;
}

.logo-text {
  @include scale.h5;
  text-decoration: none;
}

/** === Navigation Links === */

.page-links,
.section-links {
  padding: 0em;
  list-style: none;
}

.page-links {
  @include color.dynamic-theme(("inherit", false), (scale.$mobile-width, "light"));
}

.invert .page-links {
  @include color.dynamic-theme(("inherit", false), (scale.$mobile-width, "dark"));
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

@media only screen and (min-width: scale.$mobile-width) {

  .navigation-burger {
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
    @include scale.h5;
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

@media only screen and (max-width: #{ scale.$mobile-width - 1 }) {

  .page-links-container {
    position: fixed;
    top: $header-height;
    left: 0em;
    right: 0em;
    bottom: 0em;
    background: rgb(0 0 0 / 50%);
  }

  .page-links {
    padding: scale.size("h") scale.size("h");
  }

  .page-link {
    margin-bottom: scale.size("xl");
  }

  .page-link:last-child {
    margin-bottom: 0em;
  }

  .primary-link {
    @include scale.h4;
  }

  .dropdown {
    display: none;
  }

  .section-links-container {
    margin-top: scale.size("xl");
    border-left: solid 2px #f0f1f2;
    padding: 0em scale.size("xl");
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
    @include scale.h5;
    margin-bottom: scale.size("xxt");
  }

}
</style>
