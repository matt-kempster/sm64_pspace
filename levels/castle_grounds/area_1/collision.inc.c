const Collision castle_grounds_area_1_collision[] = {
	COL_INIT(),
	COL_VERTEX_INIT(12),
	COL_VERTEX(-979, 490, 169),
	COL_VERTEX(-554, 490, 169),
	COL_VERTEX(-554, 490, -256),
	COL_VERTEX(-979, 490, -256),
	COL_VERTEX(469, -405, 226),
	COL_VERTEX(894, -405, 226),
	COL_VERTEX(894, -405, -199),
	COL_VERTEX(469, -405, -199),
	COL_VERTEX(-213, 0, 213),
	COL_VERTEX(213, 0, 213),
	COL_VERTEX(213, 0, -213),
	COL_VERTEX(-213, 0, -213),
	COL_TRI_INIT(SURFACE_DEFAULT, 6),
	COL_TRI(0, 1, 2),
	COL_TRI(0, 2, 3),
	COL_TRI(4, 5, 6),
	COL_TRI(4, 6, 7),
	COL_TRI(8, 9, 10),
	COL_TRI(8, 10, 11),
	COL_TRI_STOP(),
	COL_WATER_BOX_INIT(1),
	COL_WATER_BOX(0x00, -1513, -674, 1513, 674, -609),
	COL_END()
};
