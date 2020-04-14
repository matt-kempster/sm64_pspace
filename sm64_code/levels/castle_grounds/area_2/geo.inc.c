const GeoLayout castle_grounds_area_2_Level[] = {
    GEO_NODE_START(),
    GEO_OPEN_NODE(),
        GEO_ANIMATED_PART(1, 0, 0, 0, NULL),
        GEO_OPEN_NODE(),
            GEO_ANIMATED_PART(1, 0, 0, 0, NULL),
            GEO_OPEN_NODE(),
                GEO_ANIMATED_PART(1, 400, 0, 0, castle_grounds_Traverse_mesh),
                GEO_ANIMATED_PART(1, -282, -450, 0, castle_grounds_Open_mesh),
                GEO_ANIMATED_PART(1, 1082, 450, 0, castle_grounds_Close_mesh),
            GEO_CLOSE_NODE(),
        GEO_CLOSE_NODE(),
    GEO_CLOSE_NODE(),
    GEO_RETURN(),
};
const GeoLayout castle_grounds_area_2_level[] = {
    GEO_NODE_SCREEN_AREA(10, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2),
    GEO_OPEN_NODE(),
        GEO_ZBUFFER(0),
        GEO_OPEN_NODE(),
            GEO_NODE_ORTHO(100.0000),
            GEO_OPEN_NODE(),
                GEO_BACKGROUND(BACKGROUND_ABOVE_CLOUDS, geo_skybox_main),
            GEO_CLOSE_NODE(),
        GEO_CLOSE_NODE(),
        GEO_ZBUFFER(1),
        GEO_OPEN_NODE(),
            GEO_CAMERA_FRUSTUM_WITH_FUNC(45.0000, 100, 30000, geo_camera_fov),
            GEO_OPEN_NODE(),
                GEO_CAMERA(1, 0, 0, 0, 0, -213, 0, geo_camera_main),
                GEO_OPEN_NODE(),

                    GEO_ASM(   0, geo_movtex_pause_control),
                    GEO_ASM(0x1601, geo_movtex_draw_nocolor),
                    GEO_ASM(0x1601, geo_movtex_draw_water_regions),

                    GEO_BRANCH(1, castle_grounds_area_2_Level),
                    GEO_RENDER_OBJ(),
                    GEO_ASM(0, geo_envfx_main),
                GEO_CLOSE_NODE(),
            GEO_CLOSE_NODE(),
        GEO_CLOSE_NODE(),
        GEO_DISPLAY_LIST(0, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(1, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(2, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(3, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(4, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(5, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(6, castle_grounds_material_revert_render_settings),
        GEO_DISPLAY_LIST(7, castle_grounds_material_revert_render_settings),
    GEO_CLOSE_NODE(),
    GEO_END(),
};