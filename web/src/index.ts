import ReconnectingWebSocket from "reconnecting-websocket";

type Point = [number, number];

type BoardPath = {
	type: "path";
	points: Point[];
};

type BoardObject = BoardPath;
type OnlineUsers = string[];

type ReceivedWebsocketMessage =
	| {
			type: "INITIAL_DATA";
			data: {
				objects: BoardObject[];
			};
	  }
	| {
			type: "ADD_OBJECT";
			data: {
				object: BoardObject;
			};
	  }
	| {
			type: "GET_ONLINE_USERS_RESPONSE";
			data: {
				online_users: OnlineUsers;
			};
	  };
class Board {
	objects: BoardObject[] = [];
	currentDrawingObject?: BoardObject;
	context: CanvasRenderingContext2D;
	elementPosition: Point;
	socket: ReconnectingWebSocket;
	online_users: OnlineUsers;

	constructor(private element: HTMLCanvasElement, private boardID: string) {
		this.boardID = boardID;
		const context = element.getContext("2d");
		if (context) {
			this.context = context;
			const { x, y } = element.getBoundingClientRect();
			this.elementPosition = [x, y];
		} else {
			throw new Error("Failed to get 2D context for the canvas element.");
		}
		const scheme = window.location.protocol === "http:" ? "ws" : "wss";
		this.socket = new ReconnectingWebSocket(
			`${scheme}://${window.location.host}/board/${this.boardID}`
		);
		this.socket.addEventListener("message", this.onSocketMessage);
		this.socket.addEventListener("close", this.onSocketClose);
	}

	onSocketMessage = (event: MessageEvent) => {
		const data = event.data;
		const payload = JSON.parse(data) as ReceivedWebsocketMessage;
		console.log(payload.type);
		
		if (payload.type === "INITIAL_DATA") {
			console.log(payload.data);
			this.objects = payload.data.objects;
			this.draw();
			this.getOnlineUsers();

		} else if (payload.type === "ADD_OBJECT") {
			this.objects.push(payload.data.object);
			this.draw();
			this.getOnlineUsers();

		} else if (payload.type === "GET_ONLINE_USERS_RESPONSE") {
			this.online_users = payload.data.online_users;
			this.updateUserCount();
		}
	};
	getOnlineUsers = () => {
		if (this.socket.readyState === ReconnectingWebSocket.OPEN) {
			this.socket.send(
				JSON.stringify({
					type: "GET_USERS",
				})
			);
		}
	};

	onSocketClose = (event: any) => {
		this.getOnlineUsers();
	};

	sendBoardObject = (obj: BoardObject) => {
		this.socket.send(
			JSON.stringify({
				type: "ADD_OBJECT",
				data: {
					object: this.currentDrawingObject,
				},
			})
		);
	};
	onMouseDown = (event: MouseEvent) => {
		const x = event.clientX - this.elementPosition[0];
		const y = event.clientY - this.elementPosition[1];

		this.currentDrawingObject = {
			type: "path",
			points: [[x, y]],
		};
		this.draw();
	};
	onMouseUp = () => {
		if (this.currentDrawingObject) {
			this.objects.push(this.currentDrawingObject);
			this.sendBoardObject(this.currentDrawingObject);
			this.currentDrawingObject = undefined;
			this.draw();
			this.getOnlineUsers();
		}
	};
	onMouseMove = (event: MouseEvent) => {
		const x = event.clientX - this.elementPosition[0];
		const y = event.clientY - this.elementPosition[1];
		if (!this.currentDrawingObject) return;
		if (this.currentDrawingObject.type === "path") {
			this.currentDrawingObject.points.push([x, y]);
		}
		this.draw();
	};
	updateUserCount = () => {
		let user_count = String(this.online_users?.length || 0);
		console.log(user_count);
		let doc_element = document.getElementById("show_users_count");
		if (doc_element) {
			doc_element.innerText = user_count;
		}
	};
	draw = () => {
		const { context, element } = this;
		const { width, height } = element.getBoundingClientRect();

		this.context.clearRect(0, 0, width, height);
		for (const obj of this.objects) {
			this.boardObject(obj);
		}
		if (this.currentDrawingObject) {
			this.boardObject(this.currentDrawingObject);
		}
	};

	boardObject = (obj: BoardObject) => {
		if (obj.type === "path") {
			this.boardPath(obj);
		}
	};
	boardPath = (obj: BoardPath) => {
		// console.log(obj)
		if (obj.points.length === 0) return;
		const context = this.context;
		context.beginPath();
		context.strokeStyle = "black";
		context.lineWidth = 1;
		const firstPoint = obj.points[0];
		const rest = obj.points.slice(1);
		context.moveTo(firstPoint[0], firstPoint[1]);

		for (const point of rest) {
			const [x, y] = point;
			context.lineTo(x, y);
		}
		context.stroke();
		context.closePath();
	};
	run = () => {
		this.element.addEventListener("mousedown", this.onMouseDown);
		this.element.addEventListener("mouseup", this.onMouseUp);
		this.element.addEventListener("mousemove", this.onMouseMove);
		this.element.addEventListener("mouseleave", this.onMouseUp);
		this.draw();
	};
}
const element = document.getElementById("whiteboard") as HTMLCanvasElement;
const board = new Board(element, (window as any).boardID);
board.run();
