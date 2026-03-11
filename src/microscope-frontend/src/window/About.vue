<template>
  <div class="aboutPage">
    <div class="content">
        <h1 class="mainTitle">Cellular Imaging Studio</h1>

        <div class="section">
            <p class="version"><strong>App Version:</strong> 1.0.0</p>
        </div>

        <div class="section">
            <h2 class="sectionTitle">Device Information</h2>
            <div class="infoGrid">
                <p><strong>Device Name:</strong> openflexure.microscopef3a9b2d7</p>
                <p><strong>Server Version:</strong> 2.11.0</p>
                <p><strong>Camera:</strong> openflexure.microscopef3a9b2d7</p>
                <p><strong>Stage:</strong> 2.11.0</p>
            </div>
        </div>

        <div class="section">
            <h2 class="sectionTitle">Software Information</h2>
            <div class="infoGrid">
                <p>python 3.11.10</p>
                <p>numpy 2.1.2</p>
                <p>opencv 4.10.0.84</p>
                <p>torch 2.4.1</p>
            </div>
        </div>

        <div class="section">
            <h2 class="sectionTitle">Links</h2>     
            <div class="infoGrid">
                <p>
                  <a class="report-link" href="https://docs.google.com/forms/d/e/1FAIpQLSegUnN5GF0ICj0CRlQ6HM50yFV_nvg_X8xL2ib5RbB1xKAfnA/viewform"
                  target="_blank" rel="noopener noreferrer">Report an issue</a>
                </p>
            </div>
        </div>

    </div>
  </div>
</template>

<script setup>
// Basic setup
</script>

<style scoped>
.aboutPage {
  padding: 20px;
  height: calc(100vh - 36px);
  background: var(--content-bg);
  display: flex;
  justify-content: left;
  align-items: flex-start;
  overflow-y: auto;
}

.content {
  width: 100%;
  padding: 15px;
  color: #333;
}

/* Main Title */
.mainTitle {
  color: #1f4b7a;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

/* Section Styling */
.section {
  margin: 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #B3B3B3;
}

.section:last-child {
  border-bottom: none;
}

.sectionTitle {
  color: #1f4b7a;
  font-size: 1.1rem;
  font-weight: 600;
  margin-block-start: 0.45em;
  margin-block-end: 0.4em;

}

/* Info Grid */
.infoGrid {
  display: grid;
}

.infoGrid p {
  margin: 0;
  font-size: 0.7rem;
  line-height: 1.5;
}

.infoGrid strong {
  color: #333;
  font-weight: 700;
  margin-right: 8px;
}

.report-link:visited {
  color: #0057b4;
}

/* Version */
.version {
  font-size: 0.7rem;
  color: #333;
  margin: 0;
  padding: 0;
  padding-top: 5px;
}

.version strong {
  color: #333;
}

</style>