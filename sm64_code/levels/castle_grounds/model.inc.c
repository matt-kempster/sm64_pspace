static const Lights0 castle_grounds_sm64_material_lights = gdSPDefLights0(
    0xBB, 0x9F, 0x74);

const Gfx mat_castle_grounds_sm64_material[] = {
    gsDPPipeSync(),
    gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
    gsSPTexture(65535, 65535, 0, 0, 1),
    gsDPSetEnvColor(187, 101, 132, 255),
    gsSPSetLights0(castle_grounds_sm64_material_lights),
    gsSPEndDisplayList(),
};
static const Vtx castle_grounds_Open_mesh_vtx[] = {
    { { { -213, 0, 213 }, 0, {0xFFF0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0, 213 }, 0, {0x3F0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0,  -213 }, 0, {0x3F0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { -213, 0,  -213 }, 0, {0xFFF0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
};

const Gfx castle_grounds_Open_mesh_tri_0[] = {
    gsSPVertex(castle_grounds_Open_mesh_vtx + 0, 4, 0),
    gsSP1Triangle(0, 1, 2, 0),
    gsSP1Triangle(0, 2, 3, 0),
    gsSPEndDisplayList(),
};

const Gfx castle_grounds_Open_mesh[] = {
    gsSPDisplayList(mat_castle_grounds_sm64_material),
    gsSPDisplayList(castle_grounds_Open_mesh_tri_0),
    gsDPPipeSync(),
    gsSPSetGeometryMode(G_LIGHTING),
    gsSPClearGeometryMode(G_TEXTURE_GEN),
    gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
    gsSPTexture(65535, 65535, 0, 0, 0),
    gsSPEndDisplayList(),
};

static const Vtx castle_grounds_Traverse_mesh_vtx[] = {
    { { { -213, 0, 213 }, 0, {0xFFF0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0, 213 }, 0, {0x3F0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0,  -213 }, 0, {0x3F0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { -213, 0,  -213 }, 0, {0xFFF0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
};

const Gfx castle_grounds_Traverse_mesh_tri_0[] = {
    gsSPVertex(castle_grounds_Traverse_mesh_vtx + 0, 4, 0),
    gsSP1Triangle(0, 1, 2, 0),
    gsSP1Triangle(0, 2, 3, 0),
    gsSPEndDisplayList(),
};

const Gfx castle_grounds_Traverse_mesh[] = {
    gsSPDisplayList(mat_castle_grounds_sm64_material),
    gsSPDisplayList(castle_grounds_Traverse_mesh_tri_0),
    gsDPPipeSync(),
    gsSPSetGeometryMode(G_LIGHTING),
    gsSPClearGeometryMode(G_TEXTURE_GEN),
    gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
    gsSPTexture(65535, 65535, 0, 0, 0),
    gsSPEndDisplayList(),
};

static const Vtx castle_grounds_Close_mesh_vtx[] = {
    { { { -213, 0, 213 }, 0, {0xFFF0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0, 213 }, 0, {0x3F0, 0x3F0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { 213, 0,  -213 }, 0, {0x3F0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
    { { { -213, 0,  -213 }, 0, {0xFFF0, 0xFFF0}, {0x0, 0x7F, 0x0, 0xFF} } },
};

const Gfx castle_grounds_Close_mesh_tri_0[] = {
    gsSPVertex(castle_grounds_Close_mesh_vtx + 0, 4, 0),
    gsSP1Triangle(0, 1, 2, 0),
    gsSP1Triangle(0, 2, 3, 0),
    gsSPEndDisplayList(),
};

const Gfx castle_grounds_Close_mesh[] = {
    gsSPDisplayList(mat_castle_grounds_sm64_material),
    gsSPDisplayList(castle_grounds_Close_mesh_tri_0),
    gsDPPipeSync(),
    gsSPSetGeometryMode(G_LIGHTING),
    gsSPClearGeometryMode(G_TEXTURE_GEN),
    gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
    gsSPTexture(65535, 65535, 0, 0, 0),
    gsSPEndDisplayList(),
};

const Gfx castle_grounds_material_revert_render_settings[] = {
    gsDPPipeSync(),
    gsSPSetGeometryMode(G_LIGHTING),
    gsSPClearGeometryMode(G_TEXTURE_GEN),
    gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
    gsSPTexture(65535, 65535, 0, 0, 0),
    gsDPSetEnvColor(255, 255, 255, 255),
    gsDPSetAlphaCompare(G_AC_NONE),
    gsSPEndDisplayList(),
};
