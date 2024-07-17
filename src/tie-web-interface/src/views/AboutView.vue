<template>
  <div class="about">
    <div class="about-contents">
      <h1>This is an about page</h1>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

.about {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: scale.size("xxh") 0em;
}

.about-contents {
  display: flex;
  width: 100%;
  max-width: scale.$max-width;
}
</style>
