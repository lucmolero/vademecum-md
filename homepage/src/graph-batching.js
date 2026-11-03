import {
  ConeGeometry,
  CylinderGeometry,
  InstancedMesh,
  Matrix4,
  SphereGeometry,
  Color,
} from 'three';

function graphObjects(graph) {
  const nodes = [];
  const links = [];
  const arrows = [];
  graph.scene().traverse(object => {
    if (!object.isMesh) return;
    if (object.__graphObjType === 'node') nodes.push(object);
    else if (object.__graphObjType === 'link') links.push(object);
    else if (object.__linkThreeObjType === 'arrow') arrows.push(object);
  });
  return {nodes, links, arrows};
}

function updateInstance(mesh, source, index, matrix, scaleMatrix, {radius = 1, color = true} = {}) {
  source.updateMatrixWorld(true);
  matrix.copy(source.matrixWorld);
  if (radius !== 1) {
    scaleMatrix.makeScale(radius, radius, radius);
    matrix.multiply(scaleMatrix);
  }
  mesh.setMatrixAt(index, matrix);
  if (color) mesh.setColorAt(index, new Color(source.material.color.getHex()));
}

function batchMaterial(source, opacity) {
  const material = source.material.clone();
  material.color.setHex(0xffffff);
  material.opacity = opacity;
  material.transparent = opacity < 1 || source.material.transparent;
  return material;
}

function createBatch(scene, geometry, material, sources, matrix, scaleMatrix, {radiusOf} = {}) {
  const mesh = new InstancedMesh(geometry, material, sources.length);
  mesh.name = `graph-batch-${geometry.type.toLowerCase()}`;
  mesh.frustumCulled = false;
  // Picking stays on the original, per-record meshes so graph clicks and
  // citation inspection continue to use the library's exact hit testing.
  mesh.raycast = () => {};
  sources.forEach((source, index) => updateInstance(mesh, source, index, matrix, scaleMatrix, {radius: radiusOf?.(source) || 1}));
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  scene.add(mesh);
  return mesh;
}

export function createGraphBatcher(graph, {nodeResolution = 6, arrowResolution = 5} = {}) {
  const scene = graph.scene();
  const {nodes, links, arrows} = graphObjects(graph);
  if (!nodes.length || !links.length || !arrows.length) return null;

  scene.updateMatrixWorld(true);
  const sources = [...nodes, ...links, ...arrows];
  const originalVisibility = new Map(sources.map(source => [source.material, source.material.visible]));
  const nodeRadius = source => Number(source.geometry.parameters?.radius) || 1;
  const matrix = new Matrix4();
  const scaleMatrix = new Matrix4();

  const nodeBatch = createBatch(
    scene,
    new SphereGeometry(1, nodeResolution, nodeResolution),
    batchMaterial(nodes[0], nodes[0].material.opacity),
    nodes,
    matrix,
    scaleMatrix,
    {radiusOf: nodeRadius}
  );
  const linkParameters = links[0].geometry.parameters;
  const linkBatch = createBatch(
    scene,
    new CylinderGeometry(linkParameters.radiusTop, linkParameters.radiusBottom, linkParameters.height, linkParameters.radialSegments, linkParameters.heightSegments, linkParameters.openEnded),
    batchMaterial(links[0], links[0].material.opacity),
    links,
    matrix,
    scaleMatrix
  );
  const arrowParameters = arrows[0].geometry.parameters;
  const arrowBatch = createBatch(
    scene,
    new ConeGeometry(arrowParameters.radius, arrowParameters.height, arrowResolution, arrowParameters.heightSegments, arrowParameters.openEnded, arrowParameters.thetaStart, arrowParameters.thetaLength),
    batchMaterial(arrows[0], Math.min(1, arrows[0].material.opacity)),
    arrows,
    matrix,
    scaleMatrix
  );

  sources.forEach(source => { source.material.visible = false; });
  let disposed = false;

  return {
    syncTransforms() {
      if (disposed) return;
      scene.updateMatrixWorld(true);
      nodes.forEach((source, index) => updateInstance(nodeBatch, source, index, matrix, scaleMatrix, {radius: nodeRadius(source), color: false}));
      links.forEach((source, index) => updateInstance(linkBatch, source, index, matrix, scaleMatrix, {color: false}));
      arrows.forEach((source, index) => updateInstance(arrowBatch, source, index, matrix, scaleMatrix, {color: false}));
      [nodeBatch, linkBatch, arrowBatch].forEach(mesh => {
        mesh.instanceMatrix.needsUpdate = true;
      });
    },
    syncColors({nodeColor, linkColor} = {}) {
      if (disposed) return;
      nodes.forEach((source, index) => {
        if (nodeColor) source.material.color.set(nodeColor(source.__data));
        nodeBatch.setColorAt(index, new Color(source.material.color.getHex()));
      });
      for (const [mesh, originals] of [[linkBatch, links], [arrowBatch, arrows]]) {
        originals.forEach((source, index) => {
          if (linkColor) source.material.color.set(linkColor(source.__data));
          mesh.setColorAt(index, new Color(source.material.color.getHex()));
        });
      }
      [nodeBatch, linkBatch, arrowBatch].forEach(mesh => {
        if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      });
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      sources.forEach(source => {
        source.material.visible = originalVisibility.get(source.material) ?? true;
      });
      [nodeBatch, linkBatch, arrowBatch].forEach(mesh => {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
      });
    },
  };
}
